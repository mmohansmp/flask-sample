from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return '''
    <html>
        <center><h1>This is sample app from a container </h1> </center>
    </html>

    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
    