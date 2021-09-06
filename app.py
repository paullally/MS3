import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
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
def test():
    return render_template('login.html')

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
                
        if password != check:
            flash("passwords are not equal")
            return redirect(url_for("register")) 

        mongo.db.users.insert_one({
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password"))
        })
        session["user"] = request.form.get("username")
        flash("Registration Successful!")
    return render_template("register.html")

@app.route("/login",methods=["GET", "POST"])
def login():
     if request.method == "POST":

        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username")
                return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

     return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    file = mongo.db.files.find({"id": session["user"]})
    print(file)
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username ,files=file)

@app.route('/Upload/<username>', methods=['POST'])
def upload(username):
    profile_image = request.files['profile_image']
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    test = mongo.db.files.find_one({"id": session["user"]})
    if not test:
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return "<h1>DonE!!!</h1>"
    else:
        return "<h1>error</h1>"

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)