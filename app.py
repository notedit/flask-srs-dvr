# -*- coding: utf-8 -*-
# author: llx

import uuid
import hmac
import hashlib
import base64
import time

from flask import Flask
from flask import jsonify

app = Flask(__name__)


@app.route("/api/dvrs", methods=['GET','POST'])
def on_dvrs():

    print request.values.to_dict()

    return 'ok'

if __name__ == "__main__":
    app.run()
