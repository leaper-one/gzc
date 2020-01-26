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
import pressone_config
from assets import CNB

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

    sig = prs_utility.sign_block_data(data, private_key=pressone_config.private_key)
    post_url = 'https://press.one/api/v2/datasign'

    payload = {
        'user_address': pressone_config.address,
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
