import os
import hashlib
import prs_lib
import prs_utility
import uuid
import mixin_config
from mixin_api import MIXIN_API
from mixin_ws_api import MIXIN_WS_API

from flask import Flask, render_template, g, request, redirect, session, url_for, flash, Blueprint
from flask_restful import Api, Resource

from flask_wtf import FlaskForm
from flask_uploads import UploadSet, configure_uploads, patch_request_class, DEFAULTS, ALL
# from wtforms import TextField, BooleanField, PasswordField, TextAreaField, validators

from Crypto.PublicKey import RSA

import requests
import json
import time
from io import BytesIO
import base64
import gzip

import csv
from flask_sqlalchemy import SQLAlchemy
from contextlib import closing

import prs_utility

from flask_login import LoginManager


# import DataBaseCursor
import random, string


# DATABASE = "E:/PRJCT/nbsw/tmp/nbsw.db"
# DEBUG = True
# SECRET_KEY = 'nbswl'
# USERNAME = 'admin'
# PASSWORD = 'default'

# db = DataBaseCursor.DBC()

client = prs_lib.PRS({
  'env': 'dev',
  'private_key': '01e05107e3141083f66aa2ec5fa78d095115a912ca17148813b87d4313115837',
  'address': 'acd8960a52de7017059cfd6c7113f073fad2a2a2e',
  'debug': True,
})


app = Flask(__name__) # Start Flask
api = Api(app)
# app.config.from_object(__name__)
mixin_api = MIXIN_API(mixin_config)


# login_manager = LoginManager(app)
# app.config['UPLOADED_FILES_DEST'] = os.getcwd() + '/uploads' # 文件存储地址
# ALLOW_EXTENSIONS = ['md']
# app.config["SECRET_KEY"] = "sexy0756"
# app.config['UPLOADED_DEFAULT_URL'] = 'http://127.0.0.1:5000/uploads/'
# app.config['UPLOADED_FILES_URL'] = 'http://127.0.0.1:5000/uploads/'



# bp = Blueprint('uploads', __name__, url_prefix='/uploads/')
# files = UploadSet('files', ALL)
# configure_uploads(app, files)
# patch_request_class(app)

'''
关键账号
'''
LPR = '4747badf-0f01-41b8-b632-f5e3f15245fc'

'''
资产
'''
CNB = '965e5c6e-434c-3fa9-b780-c50f43cd955c'

'''
必要加密函数
'''
def pubkeyContent(inputContent):
    contentWithoutHeader = inputContent[len("-----BEGIN PUBLIC KEY-----") + 1:]
    contentWithoutTail = contentWithoutHeader[:-1 * (len("-----END PUBLIC KEY-----") + 1)]
    contentWithoutReturn = contentWithoutTail[:64] + contentWithoutTail[65:129] + contentWithoutTail[
                                                                                  130:194] + contentWithoutTail[195:]
    return contentWithoutReturn


def generateMixinAPI(private_key,pin_token,session_id,user_id,pin,client_secret):
    mixin_config.private_key       = private_key
    mixin_config.pin_token         = pin_token
    mixin_config.pay_session_id    = session_id
    mixin_config.client_id         = user_id
    mixin_config.client_secret     = client_secret
    mixin_config.pay_pin           = pin
    return MIXIN_API(mixin_config)

# mixinApiNewUserInstance = generateMixinAPI(private_key, pin_token, session_id, userid, pin,"")


class SigApi(Resource):
    def creat(self, ws, userId, conversationId, dataindata, issig=True):
        #添加到数据库 签名队列, 公证内容
        # MIXIN_WS_API.sendUserAppButton(ws, conversationId, )
        return {"issig"}


try:
    import thread
except ImportError:
    import _thread as thread


def on_message(ws, message):
    inbuffer = BytesIO(message)

    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata_injson = f.read()
    rdata_obj = json.loads(rdata_injson)
    # print("-------json object begin---------")
    # print(time.time())
    # print(rdata_obj)
    # print("-------json object end---------")
    action = rdata_obj["action"]

    if rdata_obj["data"] is not None:
        # print("data in message:", rdata_obj["data"])
        pass

    if rdata_obj["data"] is not None and rdata_obj["data"]["category"] is not None:
        # print(rdata_obj["data"]["category"])
        pass

    if action == "CREATE_MESSAGE":

        data = rdata_obj["data"]
        msgid = data["message_id"]
        typeindata = data["type"]
        categoryindata = data["category"]
        userId = data["user_id"]
        conversationId = data["conversation_id"]
        dataindata = data["data"]

        realData = base64.b64decode(dataindata)

        MIXIN_WS_API.replayMessage(ws, msgid)

        if 'error' in rdata_obj:
            return

        if categoryindata == "PLAIN_TEXT":
            realData = realData.decode('utf-8')
            print("_____-------______")
            print("dataindata",realData)
            print(type(realData))

            if dataindata:
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, "按下列按钮以进行操作")
                trace = str(uuid.uuid1())
                # 储存到数据库
                # ifsig = MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, "www.baidu.com", 'heppy')
                a = MIXIN_WS_API.sendUserPayAppButton(ws, conversationId, userId, 'CNB', CNB, 1)
                # MIXIN_WS_API.sendAppCard(ws, conversationId, userId, CNB, 1, '', 'lalaladifjsof', 'none', memo="123456")
                pay_link = "https://mixin.one/pay?recipient="+mixin_config.client_id+"&asset="+CNB+"&amount="+"1"+"&trace="+trace+"&memo=testlink"
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, pay_link)

                time.sleep(1) #等待5分钟，后期应该成轮询

                signer2paylink = mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace)
                # print(signer2paylink.get("data").get('status'))

                if True or signer2paylink.get("data").get("status") == "paid":
                    print('1111111111111111111111111111')
                    # 更改 数据库 user表单 isalreadysign 字段 为 True

                    texthash = prs_utility.keccak256(text=realData)
                    print(texthash)
                    print('222222222222222222222222222222')
                    # 根据 PRS 协议组合 block data, 并且使用 privateKey 进行签名
                    data = {
                        'file_hash': texthash,
                    }

                    private_key = '01e05107e3141083f66aa2ec5fa78d095115a912ca17148813b87d4313115837'

                    sig = prs_utility.sign_block_data(data, private_key)

                    post_url = 'https://beta.press.one/api/v2/datasign'

                    payload = {
                        'user_address': 'acd8960a52de7017059cfd6c7113f073fad2a2a2e',
                        'type': 'PUBLISH:2',
                        'meta': {
                            'uris': texthash,
                            'mime': 'text/markdown;UTF-8'
                        },
                        'data': data,
                        'hash': prs_utility.hash_block_data(data),
                        'signature': sig
                    }
                    print('333333333333333333333333333333333')
                    req = requests.post(post_url, json=payload)
                    print(req)
                    print('44444444444444444444444444444')
                    print('signature:', sig)
                    print('555555555555555555555555555555555555')



                else:
                    MIXIN_WS_API.sendUserText(ws, conversationId, userId, pay_link)




if __name__ == "__main__":

    # mixin_api = MIXIN_API(mixin_config)
    while True:
        mixin_ws = MIXIN_WS_API(on_message=on_message)
        mixin_ws.run()
