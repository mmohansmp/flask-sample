from fabric.api import run, put
from fabric.api import env, sudo
import config
import jinja2, os
from logger import log, error
from models import *
from fabric.api import settings
from fabric.network import disconnect_all
import time



l_cfg = config.Manager('UAT')
r_cfg = config.Manager('RDS')
p_cfg = config.Manager('PROXY')
app_remote_path = config.Manager('APP_REMOTE_PATH')
app_local_path = config.Manager('APP_LOCAL_PATH')
app_install = config.Manager('APP_INSTALL')



env.host_string = ""
env.user = 'root'
env.password = 'hope4best'






def upload_rpm(sm, cm):
    if sm in ['sm_1.28.0', 'sm_1.29.0', 'sm_1.30.0'] and cm in ['cm_1.28.0', 'cm_1.29.0', 'cm_1.30.0']:
        log('Uploading service manager and case manager file from jump server to application server')
        log('service manager local path: %s case manager local path: %s' % (app_local_path.get(sm), app_local_path.get(cm)))
        service_manager_local_path = app_local_path.get(sm)
        case_manager_local_path = app_local_path.get(cm)
        remote_path_to_copy = app_remote_path.get('remote_path_to_copy')

        
        upload_sm = put('%s' %(service_manager_local_path), '%s' % (remote_path_to_copy))

        if not upload_sm.succeeded:
            print 'Uploading Service Manager rpm file has failed!, please check the file path/location'
            log('Uploading Service Manger rpm file has been failed')
            return False

        upload_cm = put('%s' % (case_manager_local_path), '%s' % (remote_path_to_copy))

        if not upload_cm.succeeded:
            print 'Uploading Case Manager rpm file has failed!, please check the file path/location'
            log('Uploading Case Manager rpm file has been failed')
            return False

        log('Service manger and case manager rpm file successfully uploaded on application server')

        return True


def install_rpm(sm, cm):
    log('Service Manager and Case Manager installation started')
    if sm in ['sm_1.28.0', 'sm_1.29.0', 'sm_1.30.0'] and cm in ['cm_1.28.0', 'cm_1.29.0', 'cm_1.30.0']:
        service_manager = app_install.get(sm)
        case_manager = app_install.get(cm)
        time.sleep(5)
        log('Installing service manager from application server path: %s' % (service_manager))
        sudo('yum -y localinstall %s' % (service_manager))
        time.sleep(5)
        log('Installing case manager from application server path: %s'  % (case_manager) )
        sudo('yum -y localinstall %s' % (case_manager))
        log('Service manger and case manager installation successful')
    else:
        print "version missmatch"
        log('Service Manger and Case Manager version missmatch')


def prepare_server_config(endpoint=None, database_username=None, database_password=None, ldap_ip=None, ldap_admin_password=None, domain_name=None):
    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)
    template = JINJA_ENVIRONMENT.get_template('serverConfigOverride.text')
    return template.render(endpoint=endpoint, database_username=database_username, database_password=database_password, ldap_ip=ldap_ip, ldap_admin_password=ldap_admin_password, domain_name=domain_name)


def server_config(id):
    dep = db.query(Deployments).filter(Deployments.id == id).first()
    endpoint = r_cfg.get('endpoint')  
    database_username = dep.inputs[0].client_rds_user_name#
    database_password = dep.inputs[0].client_rds_user_password#
    ldap_ip = l_cfg.get('ip') 
    ldap_admin_password = l_cfg.get('bind_pass') 
    domain_name = dep.inputs[0].domain_name#
    log('Information added in serverConfig-override.proprties file:')
    log('#Endpoint : %s' %endpoint)
    log('#database_username : %s' %database_username)
    log('#database_password : %s' %database_password)
    log('#ldap_ip : %s' %ldap_ip)
    log('#ldap_admin_password) : %s' %ldap_admin_password)
    log('#domain_name : %s' %domain_name)
    serverConfigOverrideTemplate = prepare_server_config(endpoint, database_username, database_password, ldap_ip, ldap_admin_password, domain_name)

    with open("serverConfig-override.properties", "wb") as fh:
        fh.write(serverConfigOverrideTemplate)

    log('Copying serverConfig-override.properties in location /opt/dpservice/service-manager/conf')
    upload_sco = put('serverConfig-override.properties', '/opt/dpservice/service-manager/conf')
    


    if not upload_sco.succeeded:
        print 'Uploading ServiceConfig-override file has failed!, please check the file path/location'
        log('Copying serverConfig-override.properties failed please check file path')
        return False

    log('serverConfig-override.properties successfully copied in location /opt/dpservice/service-manager/conf')



def prepare_case_config(ldap_client_pwd=None):
    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)
    template = JINJA_ENVIRONMENT.get_template('serverConfig.text')
    return template.render(ldap_client_pwd=ldap_client_pwd)

def case_config(id):
    log('under case_config function')
    dep = db.query(Deployments).filter(Deployments.id == id).first()
    ldap_client_pwd = dep.inputs[0].ldap_user_password
    log(ldap_client_pwd)
    serverConfigTemplate = prepare_case_config(ldap_client_pwd)


    with open("serverConfig.properties", "wb") as fh:
        fh.write(serverConfigTemplate)

    log('Copying serverConfig.properties in location /opt/dpservice/case-manager/conf')

    upload_sc = put('serverConfig.properties', '/opt/dpservice/case-manager/conf')

    if not upload_sc.succeeded:
        print 'Uploading ServiceConfig-override file has failed!, please check the file path/location'
        log('Copying serverConfig.properties failed please check file path')

    log('serverConfig.properties successfully copied in location /opt/dpservice/case-manager/conf')








def start_smcm():
    log('Starting service-Manger and case-manager service')

    '''
    result = run('service service-manager status|grep Active')
    print result.succeeded
    print result.stdout
    print result.stderr

    result = run('service case-manager status|grep Active')
    print result.succeeded
    print result.stdout
    print result.stderr
    '''

    try:
        sudo('service service-manager start')
        sudo('service case-manager start')
    except Exception as e:
        log('failed to start service manager and case manager, error is %s' % e.message)


    try:
        result = sudo('service service-manager status|grep \'is running\'')
        print result.succeeded
        log('Serice Manager succeeded? : %s' %result.succeeded)
        print result.stdout
        log('Serice Manager status : %s' %result.stdout)
        print result.stderr
        log('Serice Manager error status : %s' %result.stderr)

        result = sudo('service case-manager status|grep \'is running\'')
        print result.succeeded
        log('Case Manager succeeded? : %s' %result.succeeded)
        print result.stdout
        log('Case Manager status : %s' %result.stdout)
        print result.stderr
        log('Case Manager error status : %s' %result.stderr)

    except Exception as e:
        log('failed to start service manager and case manager, error is %s' % e.message)

def rollback_smcm(ip):
    
    with settings(host_string = ip):

        log('killing service-manager and case-manager')

        sudo('pkill -f service-manager')
        sudo('pkill -f service-manager')
        sudo('pkill -f case-manager')
        sudo('pkill -f case-manager')

        log('uninstalling service-manager case-manager')
        
        result = run('yum -y remove service-manager and case-manager')
        

        log('removing service-manager case-manager')

        # with cd('/tmp'):
        #     sudo('rm -rf service-manager*')
        #     sudo('rm -rf case-manager*')
        #     log('removed service-manager case-manager rpm from temp')
        sudo('rm -rf /tmp/service-manager*')
        sudo('rm -rf /tmp/case-manager*')
        log('removed service-manager case-manager rpm from temp')


        # with cd('/opt'):
        #     sudo('rm -rf dpservice*')
        #     log('removed dpservice')

        sudo ('rm -rf /opt/dpservice*')
        log('removed dpservice')

        print result.succeeded
        print result.stdout
        print result.stderr

    
        




def setup_app_server(sm, cm, id, ip):
    log('Confgiuring application server')
    with settings(host_string = ip):
        upload_rpm(sm, cm)
        time.sleep(5)
        install_rpm(sm, cm)
        time.sleep(5)
        server_config(id)
        time.sleep(5)
        case_config(id)
        start_smcm()
        disconnect_all()
        
