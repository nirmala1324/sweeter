# IMPORTING NEEDED DEPENDENCIES

# JSON web tokens - representing claims to be transferred between two parties
# ERROR: Install - 'pip install PyJWT==1.7.1'
# Downgrade the version of JWT
import jwt 
# hashing sha - generating hash values (random value in 
# exchange of the original one) to securely save something important (password - bitcoin(?))
import hashlib 
from pymongo import MongoClient # 
from datetime import (
    datetime, # representing and manipulating date and time
    # representing the difference between two dates or times
    # ( Getting the time difference )
    timedelta 
)
from flask import (
    Flask,              # routing, request handling, and template rendering among others
    jsonify,            # Creating JSON responses
    render_template,    # render HTML templates in Flask
    request,            # represent the HTTP request by the client ( from the request )
    redirect,           # redirect client to a different URL
    url_for             # generate URL for/ targeting endpoints in Flask app
)
# make sure that the filename is secure
# and do not pose security risk when handling file uploads
# + mitigating security risk - providing safe version of the filename
from werkzeug.utils import secure_filename

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

app = Flask(__name__)

# If we update the template, then the server will reload automatically
app.config['TEMPLATES_AUTO_RELOAD'] = True
# all of the profpic uploaded will be saved in static/profile_pics
app.config['UPLOAD_FOLDER'] = './static/profile_pics'

# Set the secret key for decrypting and encrypting
# commonly set in difficult key
SECRET_KEY = 'SPARTA' # NEEDED for JWT process encrypting
TOKEN_KEY = 'mytoken' # Global scope token

# DATABASE
conn = MongoClient(MONGODB_URI) # Create connection to MongoDB Cluster
db = conn[DB_NAME] # Targeting the database


# ROUTES ----------------------------------------------

# 
@app.route('/', methods = ['GET'])
def home():
    # extracting the token from cookies
    token_receive = request.cookies.get(TOKEN_KEY)
    # decrypting the important variables' value (TOKEN)
    try:
        payload = jwt.decode( # translating the token
            token_receive,
            SECRET_KEY,
            algorithms = ['HS256']
        )
        # get the user info and set them as payload
        user_info = db.users.find_one({'username': payload.get('id')})
        # after translating and get user info pass to template
        return render_template('index.html', user_info = user_info)
    # handle if the token has expired
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        # redirecting client to login endpoint with 'msg' data
        return redirect(url_for('login', msg = msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg = msg))

@app.route('/login', methods=['GET'])
def login():
    # retrieving the 'msg' data sent by home endpoint
    msg = request.args.get('msg') 
    # send the message from home() and render the login.html as well
    return render_template('login.html', msg=msg) 

@app.route('/user/<username>', methods = ['GET']) # getting the username data as well
def user(username): # receiving the username argument in username var
    # 1. Getting the token from cookies
    token_receive = request.cookies.get(TOKEN_KEY)
    # It's like session in PHP I guess
    try:
        # Translate/ decrypting the token
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms = ['HS256']
        )
        # determine whether the user is related to this page or not
        # show the page or not, the user own the page or not
        # related to editing user data (crucial)
        status = username == payload.get('id') 
        # getting the username data in database
        user_info = db.users.find_one(
            {'username': username},
            {'_id': False} # You can use 'False' or '0'
        )
        # render user.html along with sending those data
        # it's rendered when it is true user ( by status above )
        return render_template('user.html', user_info = user_info, status = status)
    # if the user not login yet, will be directed to login page still
    # following the home endpoint process
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

        
@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    # Conditions
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode('utf-8')

        return jsonify({"result": "success","token": token,})
    # if the data not found
    # password and username combination
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )


# Add user data ( register process )
@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    # retrieving data 
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # Encrypting password
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # id
        "password": password_hash,                                  # password
        "profile_name": username_receive,                           # user's name is set to their id by default
        "profile_pic": "",                                          # profile image file name
        "profile_pic_real": "profile_pics/profile_placeholder.png", # a default profile image
        "profile_info": ""                                          # a profile description
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})
    

# checking double or duplicated identity 
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # Value in variables
    username_receive = request.form.get('username_give')
    # check whether there is duplicate of username in database
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({
        'result': 'success',
        'exists': exists
    })
    
# Updating user profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    # the user needs to logged in first -> having token
    token_receive = request.cookies.get(TOKEN_KEY)
    # decrypt token
    try: 
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username = payload.get('id')
        # retrieve data sent by client
        name_receive = request.form.get('name_give')
        about_receive = request.form.get('about_give')
        # set in document
        new_doc = {
            'profile_name': name_receive,
            'profile_info': about_receive,
        }
        # conditional
        if 'file_give' in request.files:
            file = request.files.get('file_give')
            filename = secure_filename(file.filename)
            # extract extension file
            extension = filename.split('.')[-1] # get value split first from the back(?)
            file_path = f'profile_pics/{username}.{extension}'
            file.save('./static/' + file_path)
            new_doc['profile_pic'] = filename
            new_doc['profile_pic_real'] = file_path
        # do database process
        db.users.update_one(
            {'username' : username},
            {'$set': new_doc} # let user know how to do update
        )
        return jsonify({
            'result': 'success',
            'msg': 'Your profile has been updated!'
        
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

# create new content ( unggahan baru )
# Create posting
@app.route('/posting', methods=['POST'])
def posting():
    # the user needs to logged in first -> having token
    token_receive = request.cookies.get(TOKEN_KEY)
    # decrypt token
    try: 
        # find user that has relation of all of the content
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms = ['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        # fetch only date and comment
        date_receive = request.form.get('date_give')
        comment_receive = request.form.get('comment_give')
        # set it to document for database
        doc = {
            'username': user_info.get('username'),
            'profile_name': user_info.get('profile_name'),
            'profile_pic_real': user_info.get('profile_pic_real'),
            'comment': comment_receive,
            'date': date_receive
        }
        # insert data to posts database
        db.posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg': 'Posting successful'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

# Fetching posts (20 posts documents)
@app.route('/get_posts', methods = ['GET'])
def get_posts():
    # the user needs to logged in first -> having token
    token_receive = request.cookies.get(TOKEN_KEY)
    # decrypt token
    try: 
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username_receive = request.args.get('username_give')
        if username_receive == '':
            # limit fetching
            posts = list(db.posts.find({}).sort('date', -1).limit(20))
        else:
            posts = list(db.posts.find({'username': username_receive}).sort('date', -1).limit(20))
        # convert _id into string
        for post in posts:
            post['_id'] = str(post['_id'])
            # whether true the user has give like (?)
            post['count_heart'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'heart',
            })
            post['count_star'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'star',
            })
            post['count_thumbsup'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'thumbsup',
            })
            post['heart_by_me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'heart',
                'username': payload.get('id')
            }))
            post['star_by_me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'star',
                'username': payload.get('id')
            }))
            post['thumbsup_by_me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'thumbsup',
                'username': payload.get('id')
            }))
        return jsonify({
            'result': 'success',
            'msg': 'Successfully fetch all posts',
            'posts': posts
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

# like has its own likes database
# target the id of each box post
# give reaction in posts
@app.route('/update_like', methods=['POST'])
def update_like():
    # the user needs to logged in first -> having token
    token_receive = request.cookies.get(TOKEN_KEY)
    # decrypt token
    try: 
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        # fetch value id from payload (the box)
        # get the user data related to 
        user_info = db.users.find_one({"username": payload["id"]}) # whole user data IG
        post_id_receive = request.form["post_id_give"] # get id unique in each post box
        # get the reaction type
        type_receive = request.form["type_give"]
        action_receive = request.form.get('action_give') # like or unlike
        # set in document
        doc = {
            'post_id': post_id_receive,
            'username': user_info.get('username'),
            'type': type_receive,
        }
        if action_receive == 'like':
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
            
        count = db.likes.count_documents({
            'post_id': post_id_receive,
            'type': type_receive
        })
        
        return jsonify({
            'result': 'success',
            'msg': 'Updated!',
            'count': count
        })
        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)