# -*- coding: utf-8 -*-
# author: llx

import os
import uuid
import hmac
import hashlib
import base64
import time

from celery import Celery

from flask import Flask
from flask import jsonify

from flask  import request

from ucloud.ufile import config
from ucloud.ufile import putufile
from ucloud.compact import b
from ucloud.logger import logger, set_log_file
from ucloud.compact import BytesIO

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


session = requests.Session()

retries = Retry(total=2,
        backoff_factor=1,
        status_forcelist=[ 500, 502, 503, 504 ])

session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))



callback_url = 'http://localhost:5000/web/callback'

config.set_default(uploadsuffix='.ufile.ucloud.cn')
config.set_default(downloadsuffix='.ufile.ucloud.com.cn')


public_key = 'peJQ+GdSe2xZCxvxuSmArNDzfc46RF86c6xyYnIck6NkzVPqPykZKQ=='
private_key = '4d384c6bb3113cadc354891109d37635b4aa8221'

bucket_name = 'live-stream'

app = Flask('app')

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])

    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


@celery.task(name='app.upload_task')
def upload_task(appname,stream,filepath):
    print 'uploadtask ', appname, stream, filepath
    file_key = os.path.basename(filepath)
    handler = putufile.PutUFile(public_key, private_key)
    ret, resp = handler.putfile(bucket_name, file_key, filepath)
    print 'upload result ', ret, resp

    data = {
            'action':'on_upload',
            'app':appname,
            'stream':stream,
            'file_key':file_key
            }

    http_callback.delay(data)


@celery.task(name='app.http_callback')
def http_callback(data):

    res = session.post(callback_url,json=data)

    print res.text
    print data

@app.route('/api/on_dvr', methods=['GET','POST'])
def on_dvr():

    data = request.json

    print 'on_dvr ',data

    action = data['action']
    app = data['app']
    stream = data['stream']
    file = data['file']

    upload_task.delay(app,stream,file)

    return '0'


@app.route('/api/on_publish', methods=['GET','POST'])
def on_publish():

    data = request.json

    print data

    _data = {
            'action':data['action'],
            'app':data['app'],
            'stream':data['stream']
            }

    http_callback.delay(_data)

    return '0'


@app.route('/api/on_unpublish', methods=['GET','POST'])
def on_unpublish():

    data = request.json

    print data

    _data = {
            'action':data['action'],
            'app':data['app'],
            'stream':data['stream']
            }

    http_callback.delay(_data)

    return '0'


@app.route('/web/callback',methods=['GET','POST'])
def web_callback():

    print request.json

    return 'yes'


if __name__ == "__main__":
    app.run()
