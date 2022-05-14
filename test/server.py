import datetime
from flask import Flask
import time

app = Flask(__name__)


@app.route('/helo')
def hello():
    time.sleep(2)
    return {
        "msg": "success",
    }


app.run(processes=True, port=8082)
