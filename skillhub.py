from flask import Flask

app = Flask(__name__)


@app.route('/')
def index2():
    return 'Hello, World!'