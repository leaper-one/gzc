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


'''
关键账号
'''
private_key = '01e05107e3141083f66aa2ec5fa78d095115a912ca17148813b87d4313115837'

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
生成一个uuid格式的trace
'''
def genTrace():
    return str(uuid.uuid1())

'''
生成一个bot收款链接，需出入trace
'''
def genAPaylink(trace=genTrace(), memo='1'):
    return "https://mixin.one/pay?recipient="+mixin_config.client_id+"&asset="+CNB+"&amount="+"1"+"&trace="+trace+"&memo="+memo



'''
！不完善，未能启动
发现问题：所用 p1私钥和地址 应该重新生成
'''
def genAPressSignOfContra(userid, signer2, data):
    texthash = prs_utility.keccak256(text=userid+'\\n'+signer2+'\\n'+data)

    # 根据 PRS 协议组合 block data, 并且使用 privateKey 进行签名
    data = {
        'file_hash': texthash,
    }

    sig = prs_utility.sign_block_data(data, private_key)
    post_url = 'https://dev.press.one/api/v2/datasign'

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

    req = requests.post(post_url, json=payload)
    return req

