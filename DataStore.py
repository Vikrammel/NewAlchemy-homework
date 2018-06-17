"""File server"""
from flask import Flask, request, json
import secrets

app = Flask(__name__)

class UserFile:
    def __init__(self):
        self.f_size = None
        self.f_type = ''
        self.contents = None

class DataStore:
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

    def get_all_user_files(self, user):
        """gets all files that belong to user passed in, returns None if user's files don't exist"""
        try:
            return self.user_files[user]
        except:
            return None

    def put_user_file(self, user, filename, data, f_size, f_type):
        """stores file data for user/file"""
        new_file = UserFile()
        new_file.f_size = f_size
        new_file.f_type = f_type
        new_file.contents = data
        try:
            self.user_files[user][filename] = new_file
        except:
            self.user_files[user] = {filename: new_file}
            
    def delete_user_file(self, user, filename):
        """delete a users file"""
        try:
            del self.user_files[user][filename]
            return 204 #return status code for successful deletion
        except:
            return 404 #return status code for file not found

    def generate_session_id(self, user, password, num_bytes = 16):
        """generate a unique session ID for a specified user"""
        user_cred = self.get_user_creds(user)
        if user_cred is not None:
            if user_cred == password:
                token = secrets.token_hex(num_bytes)
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
        for user, curr_token in self.tokens.items():
            if token == curr_token:
                return user

    # def verify_token(self, user, token):
    #     """checks if user's token passed in with put/get/del requests is correct"""
    #     try:
    #         if token == self.tokens[user]:
    #             return 'valid'
    #         return 'invalid'
    #     except: #user not logged in; token doesn't exist on server
    #         return 'login'

def make_resp(resp_data, status_code):
    response = app.response_class(
        response=json.dumps(resp_data),
        status=status_code,
        mimetype='application/json',
        headers={'Content-Type':'application/json'}
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
        response = make_resp({'error':'Unknown error.'}, 400)
        if username is None:
            response = make_resp({'error': 'Please provide a username.'}, 400)
        elif password is None:
            response = make_resp({'error': 'Please provide a password.'}, 400)
        elif len(username) <= 3 or len(username) > 19:
            response = make_resp({'error': 'Invalid username length.'}, 400)
        elif str(username).isalnum == False:
            response = make_resp({'error': 'Invalid username characters.'}, 400)
        elif len(password) < 8:
            response = make_resp({'error': 'Password too short.'}, 400)
        elif USERS.get(username, None) is not None:
            response = make_resp({'error':'Username already in use.'}, 400)
        return response

@app.route('/login', methods=['POST'])
def login():
    """logs a user in so they can add/delete their files"""
    if not request.is_json:
        return('', 400)

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if db.get_user_creds(username) is None:
        response = make_resp({'error': 'User does not exist. Please register.'}, 403)
    elif password is None or username is None:
        response = make_resp({'error': 'Please provide a username and password.'}, 403)
    else:
        token = db.generate_session_id(username, password)
        if token is None:
            response = make_resp({'error':'Bad password'}, 403)
        else:
            response = make_resp({'token': token}, 200)
    return response

@app.route('/logout', methods=['POST'])
def logout():
    """logs a user out returning 200 OK or returns 403 Forbidden if user is not logged in"""
    if 'X-Session' in request.headers:
        req_token = request.headers['X-Session'] #get session token
        username = db.get_user_from_token(req_token) #get username token belongs to
        if username is not None:
            db.delete_token(username)
            return('', 200)
    return('', 403)

@app.route('/files', defaults={'filename': None})
@app.route('/files/<filename>', methods=['PUT', 'GET', 'DELETE'])
def put_get_file(filename):
    """stores or returns user's file passed in with request in db"""
    if 'X-Session' in request.headers:
        req_token = request.headers['X-Session'] #get session token
        username = db.get_user_from_token(req_token) #get username token belongs to
        if username is not None:
            if request.method == 'PUT':
                req_file = request.get_data() #get binary file data
                if req_file is None:
                    req_file = request.data
                if 'Content-Length' in request.headers and \
                     'Content-Type' in request.headers:
                    db.put_user_file(username, filename, req_file, 
                        request.headers['Content-Length'], 
                        request.headers['Content-Type'])
                    response = app.response_class(
                        response='',
                        status=201,
                        headers={'location': '/files/' + filename}
                    )
                    return response
                """specification for dealing with no Content-Type and Content-Length not provided,
                    so I decided to return 400 Bad Request with JSON response with 'error' property
                    in the same fashion as other error responses in the specification"""
                response = make_resp({'error':"Please provide 'Content-Length' and 'Content-Type' headers."}, 400)
                return response
            elif request.method == 'GET':
                if filename is not None:
                    resp_file = db.get_user_file(username, filename)
                    if resp_file is not None:
                        response = app.response_class(
                            response=resp_file.contents,
                            status=200,
                            headers={'Content-Length':resp_file.f_size, 
                                    'Content-Type':resp_file.f_type}
                        )
                        return response
                    return('', 404)
                user_files = db.get_all_user_files(username)
                if user_files is not None and user_files is not False:
                    files_contens = []
                    for f_name, f_obj in user_files.items():
                        files_contens.append({f_name: {'Content-Length': f_obj.f_size, 
                            'Content-Type': f_obj.f_type, 'Contents': f_obj.contents.decode('utf-8')}}) 
                    if len(files_contens) < 1: return('', 404)
                    response = make_resp(files_contens, 200)
                    return response
                #no spec for dealing with no user files, so returning 404 Not Found
                return('', 404)
            elif request.method == 'DELETE':
                status_code = db.delete_user_file(username, filename)
                return('', status_code)
    return('', 403)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
