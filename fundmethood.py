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
private_key = '10caade304e18855f82b5fd1c791c4e9ea78943e6a1a21b47a49405f3d0ee2c4'
publicKey = '7f14afd69c51cc76cced561c068174e8b2b763067c68199ea253ac80b6a31487489f2bd2927342188c4b2e3528b093bc12432f10ac77b0bf74abd945891c2cc2'
address = 'f5b47d7dc6dfd87c49c9a69aefed247d314385c5'

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
def genAPaylink(trace=genTrace(), asset=CNB, amount='1', memo='1'):
    return "https://mixin.one/pay?recipient="+mixin_config.client_id+"&asset="+asset+"&amount="+amount+"&trace="+trace+"&memo="+memo



'''
对一个文本签名
'''
def sign_text(userid, signer2, data):
    texthash = prs_utility.keccak256(text=userid+r'\n'+signer2+r'\n'+data)

    data = {
        'file_hash': texthash,
    }

    sig = prs_utility.sign_block_data(data, private_key='10caade304e18855f82b5fd1c791c4e9ea78943e6a1a21b47a49405f3d0ee2c4')
    post_url = 'https://press.one/api/v2/datasign'

    payload = {
        'user_address': 'f5b47d7dc6dfd87c49c9a69aefed247d314385c5',
        'type': 'PUBLISH:2',
        'meta': {
            'uris': '',
            'mime': 'text/markdown;UTF-8'
        },
        'data': data,
        'hash': prs_utility.hash_block_data(data),
        'signature': sig.get('signature')
    }

    req = requests.post(post_url, json=payload)

    return req.json()
