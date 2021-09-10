import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from datetime import datetime as date
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

@app.route("/MyWorkouts/<username>", methods=["GET", "POST"])
def workouts(username):
    file = mongo.db.files.find({"id": session["user"]})
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"]}))
    print(workout)
    return render_template("workouts.html", username=username,files=file, workouts=workout)


@app.route("/Add-Workouts/<username>", methods=["GET", "POST"])
def addworkout(username):
    file = mongo.db.files.find({"id": session["user"]})
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if request.method == 'POST':
        mongo.db.Workouts.insert_one(
            {
                'user': session["user"],
                "Date": date.today().strftime("%d/%m/%Y"),
                'Title': request.form['Title'],
                'Routine': request.form['Routine'],
                'Difficulty': request.form['Difficulty'],
            })
    return redirect(url_for('workouts', username=username))



@app.route('/delete-workout/<username>_<workout_id>')
def deleteworkout(workout_id, username):
    mongo.db.Workouts.remove({'_id': ObjectId(workout_id)})
    return redirect(url_for('workouts', username=username))


@app.route('/edit-workout/<username>_<workout_id>')
def editworkout(workout_id, username):
    edit = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
    workout = list(mongo.db.Workouts.find({"user": session["user"]}))
    return render_template('update-workout.html', username=username, edit=edit, workouts=workout)



@app.route('/updated-workout/<username>_<workout_id>', methods=['POST'])
def updateworkout(workout_id, username):
    edit = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
    
    updates = {
             'user': session["user"],
             "Date": edit['Date'],
             'Title': request.form['Title'],
             'Routine': request.form['Routine'],
             'Difficulty': request.form['Difficulty']
        }
    mongo.db.Workouts.update({"_id": ObjectId(workout_id)}, updates)
    return redirect(url_for('workouts', username=username))

@app.route("/SharedWorkouts/<username>", methods=["GET", "POST"])
def sharedworkouts(username):
    file = mongo.db.files.find({"id": session["user"]})
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    sharedworkout = list(mongo.db.Sharedworkouts.find())
    return render_template("sharedworkouts.html", username=username, files=file, workouts=sharedworkout)


@app.route("/Add-SharedWorkouts/<username>", methods=["GET", "POST"])
def addsharedworkout(username):
    file = mongo.db.files.find({"id": session["user"]})
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if request.method == 'POST':
        mongo.db.Sharedworkouts.insert_one(
            {
                'user': session["user"],
                "Date": date.today().strftime("%d/%m/%Y"),
                'Title': request.form['Title'],
                'Routine': request.form['Routine'],
                'Difficulty': request.form['Difficulty'],
            })
    return redirect(url_for('sharedworkouts', username=username))





if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)