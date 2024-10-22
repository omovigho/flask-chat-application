import os
#import sqlite3
import time
from datetime import date

#from cs50 import SQL
from flask import Flask, redirect, render_template, session, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helper import login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connect to database 
#db = SQL("sqlite:///chat.db")
#db = sqlite3.connect('chat.db')

# Configure session to use filesystem (instead of signed cookies)
app.secret_key = ""
#app.config["SESSION_COOKIE_NAME"]  = 'tel'
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# database settings
from flask_socketio import SocketIO, emit, join_room, leave_room
import mysql.connector
from mysql.connector import Error
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

def get_db():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            port=app.config['MYSQL_PORT'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        if connection.is_connected():
            #print("Connection successful")
            return connection
    except Error as e:
        app.logger.error(f"Error while connecting to MySQL: {e}")
        return None


# image folder
files = os.getcwd()
pat = "static/photos"
path = os.path.join(files,pat)

image_extensions = {'png', 'jpg', 'gif', 'jfif', 'jpeg'}
#app.config['image_folder'] = image_folder

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""def cen():
    tel = session['tel']
    db = get_db()
    
    result = db.execute("SELECT * FROM profile WHERE telNumber=? ORDER BY id DESC LIMIT 1 ", tel)
    row = db.execute("SELECT * FROM members WHERE telNumber=? ", tel)
    name = row[0]["surName"] + " " + row[0]["firstName"]
    length = len(result)
    imag = None
    for i in range(length):
        imag  = result[i]["imageName"]
             
    if imag == None:
        imag = "/static/photos/download.png"
    else:
        pass
    
    return imag, name"""
def cen():
    tel = session['tel']
    db = get_db()
    print(f"tel number is {tel}")
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM profile WHERE telNumber=%s ORDER BY id DESC LIMIT 1", (tel,))
    result = cursor.fetchall()
    print(result)
    cursor.execute("SELECT * FROM members WHERE telNumber=%s", (tel,))
    row = cursor.fetchall()
    
    name = row[0]["surName"] + " " + row[0]["firstName"]
    print(f"Name is {name}")
    length = len(result)
    imag = None
    for i in range(length):
        imag = result[i]["imageName"]
    
    if imag is None:
        imag = "/static/photos/download.png"
    
    cursor.close()
    db.close()
    
    return imag, name



# For showing 
def showProfile(user):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Execute the query
    cursor.execute("SELECT * FROM profile WHERE telNumber=%s ORDER BY id DESC LIMIT 1", (user,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    
    length = len(result)
    picture = None
    
    for i in range(length):
        picture = result[i]["imageName"]
    
    if picture is None:
        picture = "/static/photos/download.png"
    
    return picture


def replace(str):
    value = str.replace(' ','')
    return value

# the home page route
@app.route("/")
@login_required
def index():
    tel = session["tel"]
    db = get_db()
    cursor = db.cursor(dictionary=True)  # Create a cursor
    cursor.execute("SELECT * FROM friends")
    result = cursor.fetchall()
    #unread, active = action        # for displaying unread messages numbers, and show a active status 
    # profile image and name of user
    pro, name = cen()
    # finding all friends
    result_len = len(result)
    return render_template("index.html", result =result, show=showProfile, tel = tel,  
                                    imag =pro, name=name, result_len=result_len, replace=replace)
    """return render_template("index.html", result =result, show=showProfile, tel = tel, length= length,  
                                    imag =pro, name=name, res=res, result_len=result_len, replace=replace)"""



#signup and signin route
@app.route("/signup_signin")
def signup_signin():
    return render_template("signup_signin.html")


# register route
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # Forget any user_id
    session.clear()

    # Getting user input
    firstName = request.form.get("firstName")
    surName = request.form.get("surName")
    tel = request.form.get("tel")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")  # confirming password

    # Converting password to string before hashing    
    print(f"password is {password}")
    if password:
        hash = generate_password_hash(password)
        print(f"HASH PASS {hash}")
    """ User reached route via POST (as by submitting a form via POST) """
    if request.method == "POST":
        if not tel:
            return render_template("signup_signin.html", reply="Phone number is required", state='0')
        elif not password:
           return render_template("signup_signin.html", reply="Password is required", state='0') 
        elif password != confirmation:
            return render_template("signup_signin.html", reply="Passwords do not match", state='0')
        else:
            db = get_db()
            if db is None:
                return render_template("signup_signin.html", reply="Failed to connect to the database", state='0')
            
            try:
                cursor = db.cursor(dictionary=True)  # Create a cursor
                cursor.execute("SELECT * FROM members WHERE telNumber = %s", (tel,))
                rows = cursor.fetchall()

                if len(rows) == 1:
                    return render_template("signup_signin.html", reply="This number has been used", state='2')
                else:
                    cursor.execute("SELECT NOW() as date")
                    dateTime = cursor.fetchone()

                    cursor.execute("INSERT INTO onlineusers (telNumber, last_activity) VALUES (%s, %s)", (tel, dateTime['date']))
                    cursor.execute("INSERT INTO members (firstName, surName, telNumber, password) VALUES (%s, %s, %s, %s)", (firstName, surName, tel, hash))
                    
                    db.commit()
                    cursor.close()
                    db.close()
                    
                    return render_template("signup_signin.html", reply="Account created successfully", state='1')
            except mysql.connector.Error as e:
                app.logger.error(f"Error while querying the database: {e}")
                return render_template("signup_signin.html", reply="An error occurred while registering", state='0')
    else:
        return render_template("signup_signin.html")


# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        telNumber = request.form.get("tel")
        password = request.form.get("password")
        
        print(f"telNumber is {telNumber}, password is {password}")
        if not telNumber:
            return render_template("signup_signin.html",reply="Telephone number must be provided",state='0')
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("signup_signin.html",reply="Password must be provided",state='0') 
        
        print(f"tel is {telNumber}, password is {password}")
        # Query database for telephone number
        cursor = db.cursor(dictionary=True)  # Create a cursor
        #rows = cursor.execute("SELECT * FROM members WHERE telNumber = ?", request.form.get("tel"))
        cursor.execute("SELECT * FROM members WHERE telNumber = %s", (telNumber,))
        rows = cursor.fetchall()  # Fetch all rows

        if len(rows) > 0:
            print(f"hash is {rows[0]['password']} - check - {check_password_hash(rows[0]['password'], password)} str {generate_password_hash(password)}")
        else:
            return render_template("signup_signin.html",reply="Invalid username and/or password",state='0')

        
        
        #print(f"hash is {rows[0]["password"]} - check - {check_password_hash(rows[0]["password"], password)} str {generate_password_hash(password)}")
        # Ensure telephone number exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return render_template("signup_signin.html",reply="Invalid username and/or password",state='0')
            #return redirect("/signup_signin")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["tel"] = rows[0]["telNumber"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        #cursor.close()
        #db.close()
        return render_template("signup_signin.html")
    

'''# message route
@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    db = get_db()
    """message"""
    if request.method == "POST":
        tel = session["tel"]
        #Other members list
        rows = db.execute("SELECT firstName,surName,telNumber from members")
        text = request.form.get("text")
        print(f"completely achieved type: {text}")
        return redirect("/")
    else:
        return redirect("/index")


@app.route("/message/<view>", methods=["GET", "POST"])
@login_required
def messages(view):
    db = get_db()
    tel = session["tel"]  
    tim = time.strftime("%I:%M:%S%p", time.localtime())
    today = date.today()
    dat = today.strftime("%B %d, %Y")
    row = db.execute("SELECT * FROM message")
    length = len(row)
    rout = "/message/"+ view  
    # finding all friends
    res = db.execute("SELECT * FROM friends")
    result_len = len(res)
    # profile image
    pro, name = cen()
    # When a user type and submit a message
    if request.method == "POST":
        text = request.form.get("text")
        if (text != ""):  
            
            #a = "'$tel', '$view', '$time','$date','$text','unseen' ";
            query = db.execute("SELECT * FROM message WHERE sender=? and receiver=? and date=? or (sender=? and receiver=? and date=?)",
                            tel, view, dat, view, tel, dat)
            if query:
                db.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?)",None, tel, view, tim, 'Same', text, 'unseen')
                    
            else:
                db.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?)",None, tel, view, tim, dat, text, 'unseen')
            return redirect(rout)

            
    else:
        return render_template("message.html", view=view, tel=tel, row=row, length=length, dat=dat, res=res, rout=rout,
                                                 imag=pro, name=name, show=showProfile, result_len=result_len)'''
                                                 

# message route
@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == "POST":
        tel = session["tel"]
        # Other members list
        cursor.execute("SELECT firstName, surName, telNumber FROM members")
        rows = cursor.fetchall()
        text = request.form.get("text")
        print(f"completely achieved type: {text}")
        return redirect("/")
    else:
        cursor.close()
        db.close()
        return redirect("/index")


@app.route("/message/<view>", methods=["GET", "POST"])
@login_required
def messages(view):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    tel = session["tel"]
    tim = time.strftime("%I:%M:%S%p", time.localtime())
    today = date.today()
    dat = today.strftime("%B %d, %Y")
    
    cursor.execute("SELECT * FROM message")
    row = cursor.fetchall()
    length = len(row)
    rout = "/message/" + view
    
    # Finding all friends
    cursor.execute("SELECT * FROM friends")
    res = cursor.fetchall()
    result_len = len(res)
    
    # Profile image
    pro, name = cen()
    
    # When a user types and submits a message
    if request.method == "POST":
        text = request.form.get("text")
        if text != "":  
            cursor.execute("SELECT * FROM message WHERE (sender=%s AND receiver=%s AND date=%s) OR (sender=%s AND receiver=%s AND date=%s)",
                           (tel, view, dat, view, tel, dat))
            query = cursor.fetchall()
            if query:
                cursor.execute("INSERT INTO message (sender, receiver, time, date, content, status) VALUES (%s, %s, %s, %s, %s, %s)",
                               (tel, view, tim, 'Same', text, 'unseen'))
            else:
                cursor.execute("INSERT INTO message (sender, receiver, time, date, content, status) VALUES (%s, %s, %s, %s, %s, %s)",
                               (tel, view, tim, dat, text, 'unseen'))
            db.commit()
            cursor.close()
            db.close()
            return redirect(rout)
    else:
        cursor.close()
        db.close()
        return render_template("message.html", view=view, tel=tel, row=row, length=length, dat=dat, res=res, rout=rout,
                               imag=pro, name=name, show=showProfile, result_len=result_len)



@app.route("/friends")
@login_required
def friends():
    db = get_db()
    # profile image
    pro, name = cen()
    print(cen())
    tel = session["tel"]
    
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM friends")
    res = cursor.fetchall()
    result_len = len(res)
    
    # Other members list
    cursor.execute("SELECT firstName, surName, telNumber FROM members")
    rows = cursor.fetchall()
    num = len(rows)
    mem = []
    
    # Your friend request list
    friends = False
    req = "Friend Request"
    fr = []
    
    cursor.execute("SELECT * FROM friendrequest WHERE friendNumber = %s", (tel,))
    result = cursor.fetchall()
    nu = len(result)
    
    for i in range(nu):
        if result[i]["friendNumber"] == tel:
            fr.append(result[i])
            friends = True
    
    no_request = "You don't have any friend request yet."
    if not friends:
        fr.append(no_request)
    
    for j in range(num):
        if rows[j]["telNumber"] == tel:
            continue
        
        cursor.execute("SELECT * FROM friendrequest WHERE userNumber = %s AND friendNumber = %s", (rows[j]['telNumber'], tel))
        t1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM friendrequest WHERE userNumber = %s AND friendNumber = %s", (tel, rows[j]['telNumber']))
        t2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM friends WHERE userNumber = %s AND friendNumber = %s", (rows[j]['telNumber'], tel))
        t3 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM friends WHERE userNumber = %s AND friendNumber = %s", (tel, rows[j]['telNumber']))
        t4 = cursor.fetchall()
        
        if t1 or t2 or t3 or t4:
            continue
        
        mem.append(rows[j])
    
    fr_length = len(fr)
    length = len(mem)
    
    cursor.close()
    db.close()
    
    return render_template("friends.html", show=showProfile, tel=tel, res=res, result_len=result_len, name=name,
                           mem=mem, length=length, fr=fr, fr_length=fr_length, no_request=no_request, imag=pro)


@app.route("/friends/<name>")
@login_required
def add(name):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    tel = session["tel"]
    
    # Fetch user details
    cursor.execute("SELECT firstName, surName, telNumber FROM members WHERE telNumber = %s", (tel,))
    user = cursor.fetchall()
    
    if not user:
        # Handle case where user is not found
        cursor.close()
        db.close()
        return "User not found", 404

    print(user[0]["firstName"])
    
    other = "Other Members"
    
    # Fetch friend details
    cursor.execute("SELECT firstName, surName, telNumber FROM members WHERE telNumber = %s", (name,))
    friend = cursor.fetchall()
    
    if not friend:
        # Handle case where friend is not found
        cursor.close()
        db.close()
        return "Friend not found", 404

    # Check if friend request already exists
    cursor.execute("SELECT * FROM friendrequest WHERE userNumber = %s AND friendNumber = %s", (name, tel))
    result = cursor.fetchall()
    
    userName = user[0]['surName'] + ' ' + user[0]['firstName']
    friendName = friend[0]['surName'] + ' ' + friend[0]['firstName']
    
    if not result:
        cursor.execute("INSERT INTO friendrequest (friendName, friendNumber, userName, userNumber) VALUES (%s, %s, %s, %s)", 
                       (friendName, friend[0]['telNumber'], userName, user[0]['telNumber']))
        db.commit()

    cursor.close()
    db.close()
    
    return redirect("/friends")


@app.route("/friends/<remove>/<name>")
@login_required
def remove(remove, name):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    tel = session["tel"]

    # Execute delete query
    cursor.execute("DELETE FROM friendrequest WHERE userNumber=%s AND friendNumber=%s", (name, tel))
    db.commit()

    cursor.close()
    db.close()

    return redirect("/friends")


@app.route("/friends/<lop>/<confirm>/<name>")
@login_required
def confirm(lop, confirm, name):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    tel = session['tel']
    
    # Select friend requests
    cursor.execute("SELECT * FROM friendrequest WHERE friendNumber=%s", (tel,))
    result = cursor.fetchall()

    for i in range(len(result)):
        # Check if they are already friends
        cursor.execute("SELECT * FROM friends WHERE userNumber=%s AND friendNumber=%s", (tel, name))
        query = cursor.fetchall()

        if not query:
            # Insert into friends table
            cursor.execute("INSERT INTO friends (userName, userNumber, friendName, friendNumber) VALUES (%s, %s, %s, %s)",
                (result[i]["userName"], result[i]["userNumber"], result[i]["friendName"], result[i]["friendNumber"]))
            
            # Delete from friendrequest table
            cursor.execute("DELETE FROM friendrequest WHERE userNumber=%s AND friendNumber=%s", (result[i]["friendNumber"], tel))
            db.commit()

    cursor.close()
    db.close()

    return redirect("/friends")


@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    db = get_db()
    tel = session['tel']

    # When request method is post
    if request.method == "POST":
        
        image_path = os.path.join(path,tel)
        if not os.path.exists(image_path):
            os.mkdir(image_path)
        app.config['image_path'] = image_path
        image = request.files["filename"]
        img_file = secure_filename(image.filename)
        image.save(os.path.join(app.config['image_path'],img_file))
        result = db.execute("SELECT * FROM members WHERE telNumber=?", tel)
        length = len(result)
        
        name = result[0]["surName"] + " " + result[0]["firstName"]
        
        #img_folder = os.path.join(image_path,img_file)
        img_folder = "/static/photos/" + result[0]["telNumber"] + "/" + img_file
        db.execute("INSERT INTO profile VALUES(?,?,?,?)", None, name, result[0]["telNumber"], img_folder)
        return redirect("/profile")
    else:
        result = db.execute("SELECT * FROM profile WHERE telNumber=? ORDER BY id DESC LIMIT 1 ", tel)
        length = len(result)
        imag = None
        for i in range(length):
            imag  = result[i]["imageName"]
            #print(imag, " is true")
        if imag == None:
            #print("no")
            pass
        else:
            pro, nam = cen()
        
        return render_template("profile.html", imag=pro, name=nam)

    


# For logging user out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    

'''@app.route("/action", methods=["GET","POST"])
def action():
    if request.method == "POST":
        friends = request.form.get("other")
        user = request.form.get("person")
        #print(f"user is:   {user}  The end")
        #print(f"friend is:  {friends} THE END")
        

        #message notification
        if (request.form.get("action") == "unseen") :
            result = db.execute("SELECT COUNT(*) as count FROM message WHERE sender=? AND receiver=? AND status=? ", 
                                    friends, user, "unseen")
            print(result[0]['count'])
            count = result[0]['count']
            unread = str(count)
            return unread
        
        
        if (request.form.get("action") == "seen") :
                result = db.execute("UPDATE message SET status=? WHERE sender=? AND receiver=?",
                                    'seen', friends, user)
                
        
        # updating user online
        if (request.form.get("action") == "update_time") :
            result = db.execute("SELECT id FROM onlineusers WHERE telNumber=?", user)
            db.execute("UPDATE onlineusers SET last_activity = datetime('now','localtime') WHERE id = ?", result[0]["id"] )
            

        # displaying user active status
        if(request.form.get("action") == "fetch_data") :  
            result = db.execute("SELECT id FROM onlineusers WHERE last_activity > datetime('now','localtime','-10 second') AND telNumber=?", friends)
            
            #for i in range(len(result)) : 
            return str(len(result))

        return " "  '''


#from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
#from flask_sqlalchemy import SQLAlchemy
#import sqlite3
import logging


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
"""app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 5
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30"""

#db = SQLAlchemy(app)
#Session(app)
#socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app, ping_timeout=10, ping_interval=5, max_http_buffer_size=10**9)


# Setup logging
logging.basicConfig(level=logging.DEBUG)

"""def get_db():
    conn = sqlite3.connect('chat.db')
    conn.row_factory = sqlite3.Row
    return conn"""

@socketio.on('connect')
def handle_connect():
    try:
        print('Client connected')
    except Exception as e:
        app.logger.error(f'Error on connect: {e}')

@socketio.on('disconnect')
def handle_disconnect():
    try:
        print('Client disconnected')
    except Exception as e:
        app.logger.error(f'Error on disconnect: {e}')

@socketio.on('join')
def handle_join(data):
    try:
        user = data['user']
        friend = data['friend']
        room = f"{user}_{friend}"
        join_room(room)
        emit('status', {'msg': f'{user} has entered the room.'}, room=room)
    except Exception as e:
        app.logger.error(f'Error on join: {e}')

@socketio.on('leave')
def handle_leave(data):
    try:
        user = data['user']
        friend = data['friend']
        room = f"{user}_{friend}"
        leave_room(room)
        emit('status', {'msg': f'{user} has left the room.'}, room=room)
    except Exception as e:
        app.logger.error(f'Error on leave: {e}')

@socketio.on('send_message')
def handle_send_message(data):
    try:
        user = data['user']
        friend = data['friend']
        message = data['message']
        tim = time.strftime("%I:%M:%S%p", time.localtime())
        today = date.today()
        dat = today.strftime("%B %d, %Y")
        print(f"Message from {user} to {friend} is {message}")
        # Broadcast the message to the room
        room = f"{user}_{friend}"
        emit('receive_message', {'msg': message, 'user': user}, room=room, broadcast=True)

        # Insert the message into the database
        db = get_db()
        cursor = db.cursor()
        # Check if there is already a message between the same users on the same date
        query = cursor.execute(
            "SELECT * FROM message WHERE (sender=? AND receiver=? AND date=?) OR (sender=? AND receiver=? AND date=?)",
            (user, friend, dat, friend, user, dat)
        ).fetchone()

        if query:
            """cursor.execute(
                "INSERT INTO message (id, sender, receiver, time, date, content, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (None, user, friend, tim, 'Same', message, 'unseen')
            )"""
            cursor.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?)",None, user, friend, tim, 'Same', message, 'unseen')
        else:
            """cursor.execute(
                "INSERT INTO message (id, sender, receiver, time, date, content, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (None, user, friend, tim, dat, message, 'unseen')
            )"""
            cursor.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?)",None, user, friend, tim, dat, message, 'unseen')
        db.commit()
        cursor.close()
    except Exception as e:
        app.logger.error(f'Error on send_message: {e}')

        
@socketio.on('update_user_activity')
def handle_update_user_activity(data):
    try:
        user = data['user']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE onlineusers SET last_activity = NOW() WHERE telNumber = %s", (user,))
        db.commit()
    except Exception as e:
        app.logger.error(f'Error on update_user_activity: {e}')
    finally:
        cursor.close()
        db.close()

        
@socketio.on('fetch_user_login_data')
def handle_fetch_user_login_data(data):
    try:
        friend = data['friend']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM onlineusers WHERE last_activity > NOW() - INTERVAL 10 SECOND AND telNumber=%s", (friend,))
        online = cursor.fetchone() is not None
        emit('user_status', {'friend': friend, 'online': online})
    except Exception as e:
        app.logger.error(f'Error on fetch_user_login_data: {e}')
    finally:
        cursor.close()
        db.close()


@socketio.on('fetch_unread_count')
def handle_fetch_unread_count(data):
    try:
        user = data['user']
        friend = data['friend']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM message WHERE sender=%s AND receiver=%s AND status=%s", (friend, user, 'unseen'))
        unread_count = cursor.fetchone()['count']
        emit('unread_count', {'count': unread_count})
    except Exception as e:
        app.logger.error(f'Error on fetch_unread_count: {e}')
    finally:
        cursor.close()
        db.close()


@socketio.on('mark_as_seen')
def handle_mark_as_seen(data):
    try:
        user = data['user']
        friend = data['friend']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE message SET status=%s WHERE sender=%s AND receiver=%s", ('seen', friend, user))
        db.commit()
    except Exception as e:
        app.logger.error(f'Error on mark_as_seen: {e}')

if __name__ == '__main__':
    socketio.run(app, debug=True)

