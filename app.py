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

config.set_default(uploadsuffix='.ufile.ucloud.cn')
config.set_default(downloadsuffix='.ufile.ucloud.com.cn')


public_key = 'peJQ+GdSe2xZCxvxuSmArNDzfc46RF86c6xyYnIck6NkzVPqPykZKQ==' 
private_key = '4d384c6bb3113cadc354891109d37635b4aa8221'

bucket_name = 'live-stream'

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery 

celery = make_celery(app)

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

    print request.json 

    return '0'


@app.route('/api/on_unpublish', methods=['GET','POST'])
def on_unpublish():

    print request.json 

    return '0'



@celery.task()
def upload_task(appname,stream,filepath):
    print 'uploadtask ', appname, stream, filepath 

    file_key = os.path.basename(filepath)
    handler = putufile.PutUFile(public_key, private_key)
    ret, resp = handler.putfile(bucket_name, file_key, filepath)
    print 'upload result ', ret, resp 

    

if __name__ == "__main__":
    app.run()
