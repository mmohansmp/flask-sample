from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return '''
<html>
        <body style='background:#FAFAFA'>
            <center>
                <div  style='background: #C16C5A; width: 400px; height: 100px; color: white; margin: 100px; font-family: arial; font-size: 30px; box-radius: 10px'>
                    Welcome to sample flask app   <b>container</b>
                </div>
            </center>
        <body>
<html>

    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9091)
