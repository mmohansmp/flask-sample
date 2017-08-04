from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return '''
    <html>
        <body style="background: skyblue">
        <center><h1>This is sample app from a container - 01 DevOps</h1> </center>
        <body>
    </html>

    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9091)
