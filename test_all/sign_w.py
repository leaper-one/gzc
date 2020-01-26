import prs_utility
import requests

'''
PRS key pair generate by prs_utility.create_key_pair()
'''
a = prs_utility.create_key_pair()
print(a)

text_data = 'Of cause we still love you.'

def sign_text(privateKey, publicKey, address, data):
    # texthash = prs_utility.keccak256(text=userid+r'\n'+signer2+r'\n'+data)
    texthash = prs_utility.keccak256(text=text_data)

    data = {
        'file_hash': texthash,
    }

    sig = prs_utility.sign_block_data(data, a.get('privateKey'))
    post_url = 'https://press.one/api/v2/datasign'

    payload = {
        'user_address': a.get('address'),
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


r = sign_text(a.get('privateKey'), a.get('publicKey'), a.get('address'), text_data)

print(r)
