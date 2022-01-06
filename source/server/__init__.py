import flask
import threading


app = flask.Flask(__name__)

thread = threading.Thread(
    target=app.run,
    kwargs={
        "port": 8080,
        "debug": False,
        "threaded": True,
        "host": "0.0.0.0"
    }
)


@app.route("/")
def index(): return "/"