import requests, json

api_url = "http://0.0.0.0:5000"

print('\n***** User Registration Tests *****')

print('\n*** User 1 ***\n')
resp = requests.post(api_url + '/register', json={'username':'user1', 'password':'password1'}, headers={'Content-Type':'application/json'})
print(resp)
print(resp.content.decode('utf-8'))

print('\n*** Attempt to register again with user 1 credentials (should fail) ***\n')
resp = requests.post(api_url + '/register', json={'username':'user1', 'password':'password1'}, headers={'Content-Type':'application/json'})
print(resp)
print(resp.content.decode('utf-8'))

print('\n*** User 2 ***\n')
resp = requests.post(api_url + '/register', json={'username':'user2', 'password':'password2'}, headers={'Content-Type':'application/json'})
print(resp)
print(resp.content.decode('utf-8'))


print('\n\n***** Login/Logout Tests *****')

print('\n*** User 1 Valid Login ***\n')
resp = requests.post(api_url + '/login', json={'username':'user1', 'password':'password1'}, headers={'Content-Type':'application/json'})
print(resp)
print(resp.content.decode('utf-8'))

print('\n*** User 1 Valid Logout ***\n')
json_data = json.loads(resp.text)
user1_token = json_data['token']
resp = requests.post(api_url + '/logout', headers={'X-Session':user1_token})
print(resp)
print(resp.content.decode('utf-8'))


print('\n\n***** File Tests *****')

print('\n*** User 1 GET files/input_file_1.txt (should fail) ***\n')
resp = requests.post(api_url + '/login', json={'username':'user1', 'password':'password1'}, headers={'Content-Type':'application/json'})
json_data = json.loads(resp.text)
user1_token = json_data['token']
resp = requests.get(api_url + '/files/input_file_1.txt', headers={'X-Session':user1_token})
print(resp)
print(resp.content.decode('utf-8'))

print('\n*** User 1 GET all files (should fail) ***\n')
resp = requests.post(api_url + '/login', json={'username':'user1', 'password':'password1'}, headers={'Content-Type':'application/json'})
json_data = json.loads(resp.text)
user1_token = json_data['token']
resp = requests.get(api_url + '/files', headers={'X-Session':user1_token})
print(resp)
print(resp.content.decode('utf-8'))

