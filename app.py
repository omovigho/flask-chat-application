import os
import sqlite3
import time
from datetime import date

from cs50 import SQL
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
db = SQL("sqlite:///chat.db")
#db = sqlite3.connect('chat.db')

# Configure session to use filesystem (instead of signed cookies)
app.secret_key = "Daniel1234"
#app.config["SESSION_COOKIE_NAME"]  = 'tel'
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

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


def cen():
    tel = session['tel']
    result = db.execute("SELECT * FROM profile WHERE telNumber=? ORDER BY id DESC LIMIT 1 ", tel)
    row = db.execute("SELECT * FROM members WHERE telNumber=? ", tel)
    name = row[0]["surName"] + " " + row[0]["firstName"]
    length = len(result)
    imag = None
    ima = None
    #print("na name " + name) 
    for i in range(length):
        imag  = result[i]["imageName"]
        
        
    if imag == None:
        imag = "/static/photos/download.png"

    else:
        #print(imag)
        pass
    
    return imag, name


# For showing 
def showProfile(user):
    result = db.execute("SELECT * FROM profile WHERE telNumber=? ORDER BY id DESC LIMIT 1 ", user)
    length = len(result)
    picture = None
    for i in range(length):
        picture  = result[i]["imageName"]
    if picture == None:
        picture = "/static/photos/download.png"
    else:
        pass
        #print(picture)
    return picture

def replace(str):
    value = str.replace(' ','')
    return value

# the home page route
@app.route("/")
@login_required
def index():
    tel = session["tel"]
    result = db.execute("SELECT * FROM friends")
    length = len(result)
    #unread, active = action        # for displaying unread messages numbers, and show a active status 
    # profile image and name of user
    pro, name = cen()
    # finding all friends
    res = db.execute("SELECT * FROM friends")
    result_len = len(res)
    #print("image of centre is:", pro)  
    return render_template("index.html", result =result, show=showProfile, tel = tel, length= length,  
                                    imag =pro, name=name, res=res, result_len=result_len, replace=replace)



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

    # converting password to string before hashing
    password_str = str(password)      
    if password_str is not None:
        hash = generate_password_hash(password_str)

    """ User reached route via POST (as by submitting a form via POST) """
    if request.method == "POST":
        if not tel:
            return render_template("signup_signin.html",reply="Phone number is required",state='0')
        elif not password:
           return render_template("signup_signin.html",reply="Password is required",state='0') 
        elif password != confirmation:
            return render_template("signup_signin.html",reply="Password do not match", state='0')
        else:
            rows = db.execute("SELECT * FROM members WHERE telNumber = ?", tel)
            if (len(rows) == 1):
                return render_template("signup_signin.html",reply="This number have been used",state='2')
            else:
                dateTime = db.execute("SELECT datetime('now','localtime') as date")
                db.execute("INSERT INTO onlineusers (id,telNumber,last_activity) VALUES(?,?,?)", None,tel, dateTime[0]["date"])
                db.execute("INSERT INTO members (id,firstName,surName,telNumber,password) VALUES(?,?,?,?,?)", None,firstName,surName,tel,hash)
                
                return render_template("signup_signin.html", reply="Account created successfully", state='1')
    else:
        return render_template("signup_signin.html")


# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("tel"):
            return render_template("signup_signin.html",reply="Telephone number must be provided",state='0')
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("signup_signin.html",reply="Password must be provided",state='0') 


        # Query database for telephone number
        rows = db.execute("SELECT * FROM members WHERE telNumber = ?", request.form.get("tel"))

        # Ensure telephone number exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            #return render_template("signup_signin.html",reply="Invalid username and/or password",state='0')
            return redirect("/signup_signin")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["tel"] = rows[0]["telNumber"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup_signin.html")
    

# message route
@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
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
                                                 imag=pro, name=name, show=showProfile, result_len=result_len)



@app.route("/friends")
@login_required
def friends():
    # profile image
    pro, name = cen()
    print(cen())
    #print("name is " + name)
   # """message"""
    tel = session["tel"]
    res = db.execute("SELECT * FROM friends")
    result_len = len(res)
    #Other members list
    rows = db.execute("SELECT firstName,surName,telNumber from members")
    num = len(rows)
    mem = []

    #Your friend request list
    friends = False
    req =  "Friend Request"
    fr = []
    result = db.execute("SELECT * FROM friendrequest WHERE userNumber=?", tel)
    nu = len(result)
    for i in range(nu):
        if (result[i]["userNumber"] == tel ):
                #showProfile(row[3]);
                fr.append(result[i])
                friends = True   
    no_request = "You don't have any friend request yet."
    if not friends: 
        fr.append(no_request)

    
    for j in range(num):
        if (rows[j]["telNumber"] == tel):
            continue
        t1 = db.execute("SELECT * FROM friendrequest WHERE userNumber= ?  AND friendNumber= ? ", rows[j]['telNumber'], tel)
        t2 = db.execute("SELECT * FROM friendrequest WHERE userNumber= ? AND friendNumber= ?", tel, rows[j]['telNumber'])
        t3 = db.execute("SELECT * FROM friends WHERE userNumber= ? AND friendNumber= ? ", rows[j]['telNumber'], tel)
        t4 = db.execute("SELECT * FROM friends WHERE userNumber= ? AND friendNumber= ?", tel, rows[j]['telNumber'])
        if (t1 or t2 or t3 or t4):
            continue
        mem.append(rows[j])
        #showProfile(row[2]);
    
    fr_length = len(fr)
    length = len(mem)
    return render_template("friends.html", show=showProfile,tel=tel, res=res,result_len=result_len, name=name,
                        mem=mem, length=length, fr=fr, fr_length=fr_length, no_request=no_request, imag = pro)


@app.route("/friends/<name>")
@login_required
def add(name):
    tel = session["tel"]
    user = db.execute("SELECT firstName,surName,telNumber from members WHERE telNumber = ? ", tel)
    print(user[0]["firstName"])
    other =  "Other Members"
    friend = db.execute("SELECT firstName,surName,telNumber FROM members WHERE telNumber=?", name) 
    result = db.execute("SELECT * FROM friendrequest WHERE userNumber=? AND friendNumber=?", name, tel)
    userName = user[0]['surName'] + ' ' + user[0]['firstName']
    friendName = friend[0]['surName'] + ' ' + friend[0]['firstName']
    if not result:
        print(f"number is {name}")
        db.execute("INSERT INTO friendrequest VALUES(? , ?, ? , ?)", 
                    friendName,friend[0]['telNumber'],userName,user[0]['telNumber'])
         
    return redirect("/friends")


@app.route("/friends/<remove>/<name>")
@login_required
def remove(remove,name):
    print(f"remove is {name} na {remove}")
    tel = session["tel"]
    db.execute("DELETE FROM friendrequest WHERE userNumber=? AND friendNumber=?",tel, name)
    return redirect("/friends")


@app.route("/friends/<lop>/<confirm>/<name>")
@login_required
def confirm(lop,confirm,name):
    tel = session['tel']
    result = db.execute("SELECT * FROM friendrequest WHERE userNumber=?", tel)
    for i in range(len(result)):
        query = db.execute("SELECT * FROM friends WHERE userNumber=? AND friendNumber=?", tel, name)
        if not query:
            db.execute("INSERT INTO friends VALUES(?,?, ?, ?)",
                result[i]["userName"], result[i]["userNumber"], result[i]["friendName"], result[i]["friendNumber"])
            db.execute("DELETE FROM friendrequest WHERE userNumber=? AND friendNumber=?",tel, result[i]["friendNumber"])
            #print(f'{result[i]["friendNumber"]}  {result[i]["userName"]}  {result[i]["friendName"]}')
    return redirect("/friends") 


@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
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


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import logging


#socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app, ping_timeout=10, ping_interval=5, max_http_buffer_size=10**8)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def get_db():
    conn = sqlite3.connect('chat.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        cursor.execute("UPDATE onlineusers SET last_activity = datetime('now','localtime') WHERE telNumber = ?", (user,))
        db.commit()
    except Exception as e:
        app.logger.error(f'Error on update_user_activity: {e}')

@socketio.on('fetch_user_login_data')
def handle_fetch_user_login_data(data):
    try:
        friend = data['friend']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM onlineusers WHERE last_activity > datetime('now','localtime','-10 second') AND telNumber=?", (friend,))
        online = cursor.fetchone() is not None
        emit('user_status', {'friend': friend, 'online': online})
    except Exception as e:
        app.logger.error(f'Error on fetch_user_login_data: {e}')

@socketio.on('fetch_unread_count')
def handle_fetch_unread_count(data):
    try:
        user = data['user']
        friend = data['friend']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM message WHERE sender=? AND receiver=? AND status=?", (friend, user, 'unseen'))
        unread_count = cursor.fetchone()['count']
        emit('unread_count', {'count': unread_count})
    except Exception as e:
        app.logger.error(f'Error on fetch_unread_count: {e}')

@socketio.on('mark_as_seen')
def handle_mark_as_seen(data):
    try:
        user = data['user']
        friend = data['friend']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE message SET status=? WHERE sender=? AND receiver=?", ('seen', friend, user))
        db.commit()
    except Exception as e:
        app.logger.error(f'Error on mark_as_seen: {e}')

if __name__ == '__main__':
    socketio.run(app, debug=True)
