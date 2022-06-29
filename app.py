from flask import Flask, render_template, request, url_for, redirect, session, jsonify, make_response, send_file
from collections import Counter
import json
import base64
import numpy as np
from datetime import datetime


import models.model
from os import getcwd, path
#from flask_mysqldb import MySQL

model_name = "current_model"

paths ={
    "WD" : getcwd(),
    "STATIC" : path.join(getcwd(), "static"),
    "CHECKPOINT_PATH" : path.join(getcwd(), "models", model_name),
    "CONFIG_FILE" : path.join(getcwd(), "models", model_name, "pipeline.config"),
    "LABEL_MAP" : path.join(getcwd(), "models", model_name, "label_map.pbtxt")
}


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'base'

#mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    print(paths)
    if request.method == "POST":
        details = request.form
        firstName = details['firstname']
        lastName = details['lastname']
        login = details['login']
        password = details['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO administrateur(firstName, lastName, login, password) VALUES (%s, %s, %s, %s)",
                    (firstName, lastName, login, password))
        mysql.connection.commit()
        cur.close()
        print(login, password)
        if login == 'admin':
            return redirect(url_for('admin'))
        elif login == 'gerant':
            return redirect(url_for('gerant', usr=firstName))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        print(username,password)
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()

        print("connection avec succés")
        cursor.execute('SELECT * FROM administrateur WHERE login = %s AND password = %s', (username, password,))
        print('oracle')
        # Fetch one record and return result
        account = cursor.fetchone()
        print('Nous y voila')

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            # session['loggedin'] = True
            # print('test')
            # session['id'] = account['id']
            # print('test233')
            # Redirect to home page
            return render_template('admin.html')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/about')
def about():
    render_template('about.html')

@app.route('/admin')
def admin():
    return render_template('administrateur.html')

@app.route('/gestion')
def manage():
    return render_template('gestion.html')

@app.route("/image", methods=["POST"])
def getImage():
    image = request.form['file'].encode()
    filename  = request.form["filename"]
    filename = filename[:filename.index(".")]
    filename += datetime.now().strftime("%H%M%S%m%d%Y")
    filename += ".jpeg"
    imgbuf = base64.decodebytes(image)
    img_path = path.join(paths['STATIC'], f"cap/{filename}")
    print(img_path)

    with open(img_path, "wb") as fh:
        fh.write(imgbuf)
        fh.close()

        """    with open("class_map.json", 'r') as f:  
        class_map = json.load(f)
        f.close()"""
    
    model = models.model.Model(paths['CHECKPOINT_PATH'], paths['CONFIG_FILE'], paths['LABEL_MAP'])
    [labels, output_path] = model.get_predictions(img_path)

    pred = []
    for label in labels:
        pred.append(label['label'])

    imgRelPath = [reps for reps in output_path.split('/') if reps not in paths['STATIC'].split('/')]
    imgRelPath = "/" + "/".join(imgRelPath) 
    return jsonify(
        imgPath=imgRelPath,
        produits=pred
    )

@app.route("/inventaire")
def inventaire():
    imgPath = request.args.get("img")
    labels = request.args.get("produits").split(",") if request.args.get("produits") != None else list()
    labels = dict(Counter(labels)) #{'the' : 2, 'nido' : 3}
    with open("prices.json") as priceFile:
        price = json.load(priceFile)
    produit = {}
    for label in labels:
        produit.update({
            label : {
                "prixUnitaire" : price[label],
                "quantite" : labels[label],
                "prixTotal" : labels[label]*price[label]

            }
        })
    print(produit)
    return render_template("inventaire.html", imgPath=imgPath, produit=produit)

@app.route('/gerant/<usr>')
def gerant(usr):
    return f"<h1>{usr}</H1>"

if __name__ == '__main__':
    app.run(debug=True)
