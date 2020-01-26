import os
import hashlib
import mixin_config
import uuid
from mixin_api import MIXIN_API
from mixin_ws_api import MIXIN_WS_API
import prs_utility
from flask import Flask, render_template, g, request, redirect, session, url_for, flash, Blueprint
from flask_restful import Api, Resource
from Crypto.PublicKey import RSA

import requests
import json
import time
from io import BytesIO
import base64
import gzip
import prs_lib

import fundmethood as fm


app = Flask(__name__) # Start Flask
api = Api(app)
# app.config.from_object(__name__)
mixin_api = MIXIN_API(mixin_config)


@app.route('/')
def index():
    scope = 'PROFILE:READ+ASSETS:READ'
    get_auth_code_url = 'https://mixin.one/oauth/authorize?client_id=' + mixin_config.client_id + '&scope='+ scope + '&response_type=code'
    return redirect(get_auth_code_url)


@app.route('/auth')
def auth():
    auth_token1 = fm.get_auth_token()
    auth_token2 = auth_token1[0]
    print('222222222222222222222')
    print(auth_token2)
    data = mixin_api.getMyProfile(auth_token2)
    print('111111111111111111111')
    print(data)
    return data


@app.route('/happy')
def happy():
    return 'hello'


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)