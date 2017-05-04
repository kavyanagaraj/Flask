from flask import Flask, redirect, request, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5,os,binascii

app=Flask(__name__)
app.secret_key=("secret_key")
mysql = MySQLConnector(app,'mydb')

FIRST_NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
LAST_NAME_REGEX =re.compile(r'^[a-zA-Z]*$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def registration_page():
    return render_template("index.html")

@app.route('/register', methods=["POST"])
def submitted_data():
    session['ph'] = "reg"
    first_name=str(request.form["first_name"])
    last_name=str(request.form["last_name"])
    email_name=str(request.form["email_name"])
    password=str(request.form["password"])
    confirm_password=str(request.form["confirm_password"])

    if len(first_name)<2 or not FIRST_NAME_REGEX.match(first_name) or str.isalpha(first_name) != True:
        flash("The first name is too short or has invalid letters")
        return redirect('/')
    else:
        session["first_name"]=first_name
    if len(last_name)<2 or not LAST_NAME_REGEX.match(first_name) or str.isalpha(last_name)!=True:
        flash("The last name is too short or has invalid letters")
        return redirect('/')
    else:
        session["last_name"]=last_name
    if len(email_name)<2 or not EMAIL_REGEX.match(email_name):
        flash("The email is invalid")
        return redirect('/')
    else:
        session["email_name"]=email_name
    if len(password)<1:
        flash("The password is too short")
        return redirect('/')
    else:
        session["password"] = password
    if len(confirm_password)<2 or confirm_password!= session["password"]:
        flash("The passwords do not match")
        return redirect('/')

    salt =  binascii.b2a_hex(os.urandom(15))
    encrypted_pw = md5.new(password + salt).hexdigest()
    session["password"] = encrypted_pw
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at,salt) \
                VALUES(:first, :last, :email, :passw, NOW(), NOW(), :salt)"
    data = {
            'first': session['first_name'],
            'last': session['last_name'],
            'email': session['email_name'],
            'passw': session['password'],
            'salt': salt
    }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/login', methods=["POST"])
def login():
    session['ph'] = "log"
    email=str(request.form["email"])
    password=str(request.form["password"])

    query = "SELECT first_name,email,id,salt,password FROM users"
    emails = mysql.query_db(query)
    for ele in emails:
        if ele['email'] == email:
            encrypted_pw = md5.new(password + ele['salt']).hexdigest()
            if ele['password'] == encrypted_pw:
                session['uname'] = ele['first_name']
                session['uid'] = ele['id']
                return redirect('/wall')
    flash("Invalid email or password")
    return redirect('/')

@app.route('/wall')
def wall():
    query1 = "SELECT CONCAT_WS(' ', first_name, last_name) as full_name, users.id, messages.message, date_format(messages.created_at, '%M %d %Y') as date, messages.id as mid, messages.users_id as muid\
                FROM users LEFT JOIN messages on users.id = messages.users_id ORDER BY messages.created_at DESC"
    msg = mysql.query_db(query1)
    query2 = "SELECT comments.id, comments.comment as comtxt, comments.messages_id as cmsgid, comments.users_id, CONCAT_WS(' ', users.first_name, users.last_name) as full_name, date_format(comments.created_at, '%M %d %Y') as date \
                FROM comments JOIN users on users.id = comments.users_id;"
    com = mysql.query_db(query2)
    return render_template("success.html", msgs = msg, comm = com)

@app.route('/postm', methods=["POST"])
def postm():
    msg=str(request.form["message"])
    query = "INSERT INTO messages (message, created_at, updated_at, users_id) \
                    VALUES(:mess, NOW(), NOW(), :usid)"
    data = {
            'mess': msg,
            'usid': session['uid']
        }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/postcom', methods=["POST"])
def postcom():
    com = str(request.form["commenttxt"])
    msgid = request.form["msgid"]
    if com:
        query = "INSERT INTO comments (comment, created_at, updated_at, users_id,messages_id) \
                        VALUES(:comm, NOW(), NOW(), :usid, :msid)"
        data = {
                'comm': com,
                'usid': session['uid'],
                'msid': msgid
            }
        mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/deletecomm/<msguserid>')
def deletecomm(msguserid):
    query = "DELETE FROM comments WHERE comments.messages_id = :mu"
    query1 = "DELETE FROM messages WHERE messages.id = :mu"
    data = {
            'mu': msguserid
        }
    mysql.query_db(query, data)
    mysql.query_db(query1, data)
    return redirect('/wall')

@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect('/')
app.run(debug=True)
