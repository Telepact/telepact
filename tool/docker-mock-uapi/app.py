from flask import Flask
from uapi import UApiSchema

app = Flask(__name__)

@app.route('/api')
def hello_world():
    directory: str = "example/directory"
    schema = UApiSchema.from_directory(directory)
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
