import hashlib

userid = '53c81550-f7e1-4103-9501-b3147030f57a'
botid = '64abce35-ad54-4828-9e87-b2f46148b0ad'

if userid > botid:
    minID, maxID = botid, userid
else:
    minID, maxID = userid, botid

h = hashlib.md5()

print(h.hexdigest())

h = h.hexdigest()+minID+maxID

print(h)