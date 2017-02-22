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


@app.route('/api/on_dvr', methods=['GET','POST'])
def on_dvr():

    print request.values.to_dict()

    return 'ok'


@app.route('/api/on_publish', methods=['GET','POST'])
def on_publish():

    print request.values.to_dict()

    return 'ok'


@app.route('/api/on_unpublish', methods=['GET','POST'])
def on_unpublish():

    print request.values.to_dict()

    return 'ok'


if __name__ == "__main__":
    app.run()
