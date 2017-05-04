from flask import Flask, render_template, request, redirect, session
from time import gmtime, strftime
app = Flask(__name__)
app.secret_key = "adsed"
import random

@app.route('/')
def index():
    if not 'gold' in session:
        session['gold']=0
    if not 'acti' in session:
        session['acti'] = []
    if not 'switch' in session:
        session['switch'] = "true"

    return render_template("index.html", gold = session['gold'])

@app.route('/process_money', methods=['POST'])
def incre():
    session['switch'] = "true"
    if request.form['building'] == 'farm':
        gc = random.randrange(10,21)
        session['gold'] += gc
        # strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()
        session['acti'].append("Earned {} golds from the farm!".format(gc))
    elif request.form['building'] == 'cave':
        gc = random.randrange(5,11)
        session['gold'] += gc
        session['acti'].append("Earned {} golds from the cave!".format(gc))
    elif request.form['building'] == 'house':
        gc = random.randrange(2,5)
        session['gold'] += random.randrange(2,5)
        session['acti'].append("Earned {} golds from the house!".format(gc))
    elif request.form['building'] == 'casino':
        gc = random.randrange(-50,50)
        session['gold'] += gc
        if gc > 0:
            session['acti'].append("Earned {} golds from the casino!".format(gc))
        else:
            session['acti'].append("Entered a casino and lost {} golds...Ouch".format(gc*(-1)))
            session['switch'] = "false"
    return render_template("index.html", acti = session['acti'], switch = session['switch'])

@app.route('/reset', methods=['POST'])
def reset():
    session['acti'] = []
    session['gold']= 0
    return redirect('/')
app.run(debug=True)
