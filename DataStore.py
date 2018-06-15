"""File server"""
from flask import Flask, request
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
    
    def delete_token(self, user):
        """removes the session token for a given user when they log out"""
        try:
            del self.tokens[user]
        except:
            pass
    
    def verify_token(self, user, token):
        """checks if user's token passed in with put/get/del requests is correct"""
        try:
            if token == self.tokens[user]:
                return 'valid'
            return 'invalid'
        except: #user not logged in; token doesn't exist on server
            return 'login'

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
        return('User registered', 200)
    else:
        #401 = username error, 402 = pw error
        if username is None:
            return('Please provide a username', 401)
        elif password is None:
            return('Please provide a password', 402)
        elif len(username) <= 3 or len(username) > 19:
            return('Invalid username length', 401)
        elif str(username).isalnum == False:
            return('Invalid username characters', 401)
        elif len(password) < 8:
            return('Password too short', 402)


# TODO implement login/files endpoints

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
