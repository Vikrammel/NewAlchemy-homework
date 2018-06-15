"""File server"""
from flask import Flask, request, json
import base64, M2Crypto

app = Flask(__name__)

class DataStore:
    """simple in-memory filestore, fix bugs as needed"""
    def __init__(self):
        self.users = {}
        self.user_files = {}
        self.tokens = {}

    def get_user_creds(self, user):
        """gets a users credentials from the data store"""
        return self.users.get(user, None)

    def put_user_credentials(self, user, cred):
        """saves a users credentials to the data store"""
        self.users[user] = cred

    def get_user_file(self, user, filename):
        """gets a users file by name, returns None if user or file doesn't exist"""
        try:
            return self.user_files[user][filename]
        except:
            return None

    def put_user_file(self, user, filename, data):
        """stores file data for user/file"""
        self.user_files[user] = {filename: data}

    def delete_user_file(self, user, filename):
        """delete a users file"""
        try:
            del self.user_files[user][filename]
        except:
            pass

    def generate_session_id(self, user, num_bytes = 16):
        """generate a unique session ID for a specified user"""
        token = base64.b64encode(M2Crypto.m2.rand_bytes(num_bytes))
        self.tokens[user] = token
        return token
    
    def delete_token(self, user):
        """removes the session token for a given user when they log out"""
        try:
            del self.tokens[user]
        except:
            pass

    def get_user_from_token(self, token):
        """returns username of user logged in with active token passed in"""

    def verify_token(self, user, token):
        """checks if user's token passed in with put/get/del requests is correct"""
        try:
            if token == self.tokens[user]:
                return 'valid'
            return 'invalid'
        except: #user not logged in; token doesn't exist on server
            return 'login'

def make_resp(resp_data, status_code):
    response = app.response_class(
        response=json.dumps(resp_data),
        status=status_code,
        mimetype='application/json'
    )
    return response

db = DataStore()
USERS = db.users

@app.route('/register', methods=['POST'])
def register():
    """register a user with username and password"""
    if not request.is_json:
        return('', 400)

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username is not None and \
        password is not None and \
        USERS.get(username, None) is None and \
        len(username) > 3 and len(username) < 20 and \
        str(username).isalnum() and \
        len(password) >= 8: 
        db.put_user_credentials(username, password)
        return('', 204)
    else:
        if username is None:
            response = make_resp({'error': 'Please provide a username.'}, 400)
            return response
        elif password is None:
            response = make_resp({'error': 'Please provide a password.'}, 400)
            return response
        elif len(username) <= 3 or len(username) > 19:
            response = make_resp({'error': 'Invalid username length.'}, 400)
            return response
        elif str(username).isalnum == False:
            response = make_resp({'error': 'Invalid username characters.'}, 400)
            return response
        elif len(password) < 8:
            response = make_resp({'error': 'Password too short.'}, 400)
            return response

@app.route('/login', methods=['POST'])
def login():
    """logs a user in so they can add/delete their files"""
    if not request.is_json:
        return('', 400)

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if USERS.get(username, None) is None:
        response = make_resp({'error': 'User does not exist. Please register.'}, 403)
        return response
    else:
        token = db.generate_session_id(username)
        response = make_resp({'token': token}, 200)
        return response
    
# TODO implement files endpoints
# working on this, will complete tomorrow
@app.route('/files/<filename>', methods=['PUT'])
def put_file(filename):
    """stores user's file passed in with request in db"""
    if 'X-Session' in request.headers:
        print(request.headers['X-Session'])
        print('found token')
        return("", 200)
    return('', 400)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
