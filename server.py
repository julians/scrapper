from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "hello"


@app.route("/random")
def random():
    return "blah"
