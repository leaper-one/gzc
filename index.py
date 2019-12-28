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

'''
关键账号
'''
LPR = '4747badf-0f01-41b8-b632-f5e3f15245fc'

'''
资产编号
'''
CNB = '965e5c6e-434c-3fa9-b780-c50f43cd955c'

client = prs_lib.PRS({
  'env': 'dev',
  'private_key': '01e05107e3141083f66aa2ec5fa78d095115a912ca17148813b87d4313115837',
  'address': 'acd8960a52de7017059cfd6c7113f073fad2a2a2e',
  'debug': True,
})

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
            # print(type(realData))

            if dataindata:
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, "按下列按钮以进行操作")
                MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, 'https://172.20.10.2/auth?code=8045c3b7048bd4e1670716ce4503715923613f75ad836b4e3a6ca1c0710ae779&state=', 'test')

                # 储存到数据库
                # ifsig = MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, "www.baidu.com", 'heppy')
                a = MIXIN_WS_API.sendUserPayAppButton(ws, conversationId, userId, 'CNB', CNB, 1)
                # MIXIN_WS_API.sendAppCard(ws, conversationId, userId, CNB, 1, '', 'lalaladifjsof', 'none', memo="123456")
                trace = fm.genTrace()
                pay_link = fm.genAPaylink(trace)

                MIXIN_WS_API.sendUserText(ws, conversationId, userId, pay_link)

                time.sleep(1) #等待5分钟，后期应该成轮询

                signer2paylink = mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace)
                # print(signer2paylink.get("data").get('status'))

                if True or signer2paylink.get("data").get("status") == "paid": # 需要更改判断条件
                    # 获取signer2 的 mixinid
                    signer2 = ''
                    # 更改 数据库 user表单 isalreadysign 字段 为 True
                    pub_sign = fm.genAPressSignOfContra(userId,signer2,realData)
                    print(pub_sign)


                else:
                    MIXIN_WS_API.sendUserText(ws, conversationId, userId, pay_link)


@app.route('/')
def index():
    return 'hello'

# 一个 请求 回复的实例 https://mixin.one/auth?code=8045c3b7048bd4e1670716ce4503715923613f75ad836b4e3a6ca1c0710ae779&state=
'''
! 未完成
https://mixin-network.gitbook.io/mixin-network-cn/messenger-ying-yong-kai-fa/huo-qu-messenger-yong-hu-de-xin-xi
#获取messenger用户的信息

 一个 请求 回复的实例 https://mixin.one/auth?code=8045c3b7048bd4e1670716ce4503715923613f75ad836b4e3a6ca1c0710ae779&state=
以下方法 用于获取实例中的code
如有需要改动机器人跳转 OAuth_redirect url ，请务必联系 tymon
'''
@app.route('/auth', methods=['GET'])
def get_code():
    if request.method == 'GET':
        code = request.args['code']
        print(code)
    return code


if __name__ == "__main__":

    # mixin_api = MIXIN_API(mixin_config)
    while True:
        mixin_ws = MIXIN_WS_API(on_message=on_message)
        mixin_ws.run()
