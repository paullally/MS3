import os
import json
import random
import string
import uuid
from flask import Flask, flash,render_template, session, request, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from os import path
import bcrypt
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template('base.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        check = request.form.get("password2")
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username")
            })

        existing_email = mongo.db.users.find_one({
            "email": request.form.get("email")
            })

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        if existing_email:
            flash("Email already in use")
            return redirect(url_for("register"))
        
        if password is not check:
            flash("passwords are not equal")
            return redirect(url_for("register"))
            
        mongo.db.users.insert_one({
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password")
        })
        session["user"] = request.form.get("username")
        flash("Registration Successful!")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)