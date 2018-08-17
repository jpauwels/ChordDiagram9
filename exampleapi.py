# Example ChordDB API

import pymongo

client = pymongo.MongoClient('mongodb+srv://readonly:1doOzIOAZbbG8I5s@freecluster-78b1r.mongodb.net/test')
db = client.jamendo
test=db.pieces.find_one({"_id": 1235149})
print(test)


# Example Jamendo API
import requests

base_url = 'https://api.jamendo.com/'
client_id = 'f19cc536'

p = {'search': 'search term', 'client_id': client_id, 'format': 'json', 'limit': 10}
r = requests.get(base_url+'v3.0/tracks', params=p)
print(r.status_code)
print(r.json())
