from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
app.secret_key = "adbed"
mysql = MySQLConnector(app,'emailval')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def process():
    flash("Success! Your email is {}".format(session['email']))
    query = "SELECT * FROM emailtb"
    emails = mysql.query_db(query)
    return render_template("success.html", emails = emails)

@app.route("/process", methods=["POST"])
def create():
    email_name=request.form["email"]
    if len(email_name)<2 or not EMAIL_REGEX.match(email_name):
        flash("The email is invalid")
        return redirect('/')
    else:
        query= "INSERT INTO emailtb (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        session['email'] = request.form['email']
        data= {
            "email": request.form["email"]
            }
        mysql.query_db(query,data)
        return redirect('/success')

@app.route('/delete', methods=["POST"])
def delete():
    delid = request.form['delete']
    query = "DELETE FROM emailtb WHERE id = :specific_id"
    data = {'specific_id': delid}
    mysql.query_db(query, data)
    return redirect('/success')

app.run(debug=True)
