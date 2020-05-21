import requests
import json

payload = json.dumps(
  {
    "username": "MarkBiggerPP",
    "password": "MarkIsCool420"
  })

headers = {
  'Content-Type': 'application/json'
}

response = requests.post('https://team3.ppdb.me/api/users/auth', data=payload, headers=headers)

token = "Bearer {}".format(response.json()['token'])

headers = {
  'Content-Type': 'application/json',
  'Authorization': token
}

payload = json.dumps(
  {
    "from": [51.130215, 4.571509],
    "to": [51.176853, 4.835595],
    "passenger-places": 4,
    "arrive-by": "2020-05-30T10:00:00.00"
  })

response = requests.post('https://team3.ppdb.me/api/drives', data=payload, headers=headers)


print(response.status_code)
print(response.headers)
print(response.json())