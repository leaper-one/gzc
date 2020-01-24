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
    auth_token = fm.get_auth_token()
    data = mixin_api.getMyProfile(auth_token)
    return data


@app.route('/happy')
def happy():
    return 'hello'


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

'''
text 默认值
'''
# global text_with_userid
text_with_userid = None



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
        # print(userId)
        conversationId = data["conversation_id"]
        dataindata = data["data"]
        realData = base64.b64decode(dataindata)
        # print(realData.decode('utf-8'))
        MIXIN_WS_API.replayMessage(ws, msgid)
        print(categoryindata)
        print(typeindata)

        if 'error' in rdata_obj:
            return

        if categoryindata == "PLAIN_TEXT":
            realData = realData.decode('utf-8')
            print("_____-------______")
            print("dataindata",realData)
            print(userId)
            print("_____-------______")

            # print(type(realData))

            if dataindata:
                data = realData
                text_with_userid = {'userId':userId, 'data':data}
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, "按下列按钮以付款")
                # MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, 'https://172.20.10.2/auth?code=8045c3b7048bd4e1670716ce4503715923613f75ad836b4e3a6ca1c0710ae779&state=', 'test')

                # 储存到数据库
                # ifsig = MIXIN_WS_API.sendUserAppButton(ws, conversationId, userId, "www.baidu.com", 'heppy')

                # a = MIXIN_WS_API.sendUserPayAppButton(ws, conversationId, userId, 'CNB', CNB, 1)
                trace1 = fm.genTrace()
                # MIXIN_WS_API.sendAppCard(ws, conversationId, userId, CNB, 1, '', 'lalaladifjsof', 'none', memo="123456")
                MIXIN_WS_API.sendUserPayAppButton(ws, conversationId, userId, '付款以邀请对方公证', CNB, 1, trace1)
                # MIXIN_WS_API.sendUserText(ws, conversationId, userId, fm.genAPaylink(trace=trace1))

                for i in range(0,20):
                    print(mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace1).get("data").get("status"))
                    if mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace1).get("data").get("status") == "pending":
                        continue
                    time.sleep(1)
                    MIXIN_WS_API.sendUserText(ws, conversationId, userId, '请发送一个名片')
                    step1isread = True
                    time.sleep(1)
                    if mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace1).get("data").get("status") == "paid":
                        break
                    time.sleep(1)

        if categoryindata == "PLAIN_CONTACT":
            # print(locals().keys()

            # MIXIN_WS_API.sendUserText(ws, conversationId, userId, '一个名片')
            print('111111111111')
            time.sleep(1)
            # signer2 = realData.decode('utf-8')['user_id']
            signer2 = eval(realData.decode('utf-8'))['user_id']
            trace2 = fm.genTrace()

            # print(signer2)
            # new_conv_id = str(uuid.uuid1())
            # print(new_conv_id)
            # time.sleep(1)
            # r = mixin_api.createGroup(new_conv_id, 'ADD', userId, signer2)
            # time.sleep(1)
            # print(r)
            MIXIN_WS_API.sendUserText(ws, conversationId, userId, '转发以下支付链接，请对方付款以共证：')
            MIXIN_WS_API.sendUserText(ws, conversationId, userId, fm.genAPaylink(trace=trace2))

            for i in range(0, 20):
                # print(mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace2).get("data").get("status"))
                if mixin_api.verifyPayment(CNB, mixin_config.client_id, "1", trace2).get("data").get("status") == "pending":
                    print('NO')
                    continue
                else:
                    print('YES')
                    print('222222')
                    r = fm.sign_text(userId,signer2,text_with_userid.get('data'))
                    time.sleep(1)
                    print('333333333')
                    print(r)
                    text_with_userid = None

                    print('121212122')
                    time.sleep(1)
                    break
                time.sleep(1)

            print('444444444')


if __name__ == "__main__":

    # mixin_api = MIXIN_API(mixin_config)
    while True:
        mixin_ws = MIXIN_WS_API(on_message=on_message)
        mixin_ws.run()
        # app.run(debug=True, host='0.0.0.0')