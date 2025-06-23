from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Zeylo's Bot Live port. This site does NOT do anything"


if __name__ == "__main__":
    app.run()
