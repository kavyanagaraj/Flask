from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ninja')
def index2():
    return render_template("index2.html", phrase="justNinja")

@app.route('/ninja/<color>')
def ninja_color(color):
    return render_template("index2.html", phrase=color)

@app.route('/result', methods=['POST'])
def create_user():
   print "Got Post Info"
   return render_template("result.html", name = request.form['name'], location = request.form['location'],favlang = request.form['favlang'], comment = request.form['comment'])

app.run(debug=True, port=5000)
