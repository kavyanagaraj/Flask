from flask import Flask, redirect, request, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5,os,binascii

app=Flask(__name__)
app.secret_key=("secret_key")
mysql = MySQLConnector(app,'loginreg')

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
    return render_template("success.html")

@app.route('/login', methods=["POST"])
def login():
    session['ph'] = "log"
    email=str(request.form["email"])
    password=str(request.form["password"])

    query = "SELECT email,id,salt,password FROM users"
    emails = mysql.query_db(query)
    for ele in emails:
        if ele['email'] == email:
            encrypted_pw = md5.new(password + ele['salt']).hexdigest()
            if ele['password'] == encrypted_pw:
                return render_template("success.html")
    flash("Invalid email or password")
    return redirect('/')

@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect('/')
app.run(debug=True)
