"""File server"""
from flask import Flask, request

app = Flask(__name__)

class DataStore:
    """simple in-memory filestore, fix bugs as needed"""
    def __init__(self):
        self.users = {}
        self.user_files = {}

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

db = DataStore()

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
           # TODO store username/password

    #TODO handle invalid data


# TODO implement login/files endpoints

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
