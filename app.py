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
def home():
    # renders home page default link
    return render_template('home.html')


@app.route("/loginpage")
def loginpage():
    # renders log in page
    return render_template('login.html')


@app.route("/new-user")
def newuser():
    # displays register page
    return render_template('register.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """ allows users to register checks if user exists and
    passwords match before registering """
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
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # allows users to log in
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"],
               request.form.get("password")):
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


@app.route("/home/<username>")
def homeloggedin(username):
    # displays home page for logged in users
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        return render_template('homeloggedin.html', username=username,
                               files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # displays profile page
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"]}))
        return render_template("profile.html", username=username, files=file,
                               goals=goal)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/profile-completed/<username>", methods=["GET", "POST"])
def profilecompleted(username):
    # displays profile page with compelted goals
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"],
                    "Completed": "Complete"}))
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        return render_template("profile-completed.html", username=username,
                               files=file, goals=goal)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/profile-inprogress/<username>", methods=["GET", "POST"])
def profileinprogress(username):
    # displays the goal page which goals are in progress
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"],
                    "Completed": "Incomplete"}))
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        return render_template("profile-inprogress.html", username=username,
                               files=file, goals=goal)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/Upload/<username>', methods=['POST'])
def upload(username):
    # upload profile picture on main profile page
    if username == session["user"]:
        profile_image = request.files['profile_image']
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        test = mongo.db.files.find_one({"id": session["user"]})
        if not test:
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for("profile", username=username))
        else:
            mongo.db.files.remove({"id": session["user"]})
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for("profile", username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/Upload-completed/<username>', methods=['POST'])
def uploadcompleted(username):
    # upload a profile picture on the goal complete page
    if username == session["user"]:
        profile_image = request.files['profile_image']
        test = mongo.db.files.find_one({"id": session["user"]})
        if not test:
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for('profilecompleted', username=username))
        else:
            mongo.db.files.remove({"id": session["user"]})
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for('profilecompleted', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/Upload-inprogress/<username>', methods=['POST'])
def uploadinprogress(username):
    # upload a profile picture on the goal in progress page
    if username == session["user"]:
        profile_image = request.files['profile_image']
        test = mongo.db.files.find_one({"id": session["user"]})
        if not test:
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for('profileinprogress', username=username))
        else:
            mongo.db.files.remove({"id": session["user"]})
            mongo.save_file(profile_image.filename, profile_image)
            mongo.db.files.insert({'id': session["user"],
                                   'profile_image_name': profile_image.filename
                                   })
            return redirect(url_for('profileinprogress', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/file/<filename>')
def filed(filename):
    # retrieves files for profile picture
    return mongo.send_file(filename)


@app.route("/logout")
def logout():
    # function that logs user out
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/MyWorkouts/<username>", methods=["GET", "POST"])
def workouts(username):
    # displays workout page
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        workout = list(mongo.db.Workouts.find({"user": session["user"]}))
        return render_template("workouts.html", username=username, files=file,
                               workouts=workout)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/Add-Workouts/<username>", methods=["GET", "POST"])
def addworkout(username):
    # allows user to add workout
    if username == session["user"]:
        if request.method == 'POST':
            mongo.db.Workouts.insert_one(
                {
                    'user': session["user"],
                    "Date": date.today().strftime("%d/%m/%Y"),
                    'Title': request.form['Title'],
                    'Routine': request.form['Routine'],
                    'Difficulty': request.form['Difficulty'],
                    'Shared': False,
                })
        return redirect(url_for('workouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/delete-workout/<username>_<workout_id>')
def deleteworkout(workout_id, username):
    # allows user to delete a workout
    if username == session["user"]:
        mongo.db.Workouts.remove({'_id': ObjectId(workout_id)})
        return redirect(url_for('workouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-workout/<username>_<workout_id>')
def editworkout(workout_id, username):
    # allows user to edit a workout
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        edit = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
        workout = list(mongo.db.Workouts.find({"user": session["user"]}))
        return render_template('update-workout.html', username=username,
                               edit=edit, workouts=workout, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/updated-workout/<username>_<workout_id>', methods=['POST'])
def updateworkout(workout_id, username):
    # updates workout with new data
    if username == session["user"]:
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
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/SharedWorkouts/<username>", methods=["GET", "POST"])
def sharedworkouts(username):
    # displays the shared workouts page
    if username == session["user"]:
        file = list(mongo.db.files.find())
        sharedworkout = list(mongo.db.Sharedworkouts.find())
        return render_template("sharedworkouts.html", username=username,
                               files=file, workouts=sharedworkout)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/Saved-SharedWorkouts/<username>", methods=["GET", "POST"])
def savedsharedworkouts(username):
    # displays the saved shared workouts page
    if username == session["user"]:
        file = list(mongo.db.files.find())
        sharedworkout = list(mongo.db.Sharedworkouts.find())
        return render_template("savedsharedworkouts.html", username=username,
                               files=file, workouts=sharedworkout)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/Add-SharedWorkouts/<username>", methods=["GET", "POST"])
def addsharedworkout(username):
    # function that allows user to create a shared workout
    if username == session["user"]:
        if request.method == 'POST':
            saved = []
            mongo.db.Sharedworkouts.insert_one(
                {
                    'user': session["user"],
                    "Date": date.today().strftime("%d/%m/%Y"),
                    'Title': request.form['Title'],
                    'Routine': request.form['Routine'],
                    'Difficulty': request.form['Difficulty'],
                    'Savedby': saved
                })
        return redirect(url_for('sharedworkouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/delete-Sharedworkout/<username>_<workout_id>')
def deleteSharedworkout(workout_id, username):
    """ function to delete a shared workout
    only works for workouts created by user """
    if username == session["user"]:
        mongo.db.Sharedworkouts.remove({'_id': ObjectId(workout_id)})
        return redirect(url_for('sharedworkouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-Sharedworkout/<username>_<workout_id>')
def editSharedworkout(workout_id, username):
    """ function that allows user to edit a shared workout this
    will only work on the workouts the user has created """
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
        sharedworkout = list(mongo.db.Sharedworkouts.find())
        return render_template('update-Sharedworkout.html', username=username,
                               edit=edit, workouts=sharedworkout, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/update-Sharedworkout/<username>_<workout_id>',
           methods=['GET', 'POST'])
def updateSharedworkout(workout_id, username):
    # function that updates a shared workout with new information
    if username == session["user"]:
        edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
        if not request.form['Routine']:
            Routine = edit["Routine"]
        else:
            Routine = request.form['Routine']
        updates = {
                'user': session["user"],
                'Date': edit['Date'],
                'Title': request.form['Title'],
                'Routine': Routine,
                'Difficulty': request.form['Difficulty'],
                'Savedby':  edit['Savedby']
            }
        mongo.db.Sharedworkouts.update({"_id": ObjectId(workout_id)}, updates)
        return redirect(url_for('sharedworkouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/save-Sharedworkout/<username>_<workout_id>')
def saveSharedworkout(workout_id, username):
    # allows user to save a shared workout
    if username == session["user"]:
        edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
        saved = edit['Savedby']
        if session["user"] in saved:
            return redirect(url_for('sharedworkouts', username=username))
        else:
            saved.append(session["user"])
            updates = {
                    'user': edit['user'],
                    "Date": edit['Date'],
                    'Title': edit['Title'],
                    'Routine': edit['Routine'],
                    'Difficulty': edit['Difficulty'],
                    'Savedby': saved
                }
            mongo.db.Sharedworkouts.update({"_id": ObjectId(workout_id)},
                                           updates)
        return redirect(url_for('sharedworkouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/Shareexistingworkout/<username>_<workout_id>',
           methods=['GET', 'POST'])
def shareexisitingworkout(workout_id, username):
    # allows user to share a workout from workouts page to shared workouts page
    if username == session["user"]:
        share = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
        saved = []
        mongo.db.Workouts.update_one({'_id': ObjectId(workout_id)},
                                     {"$set": {"Shared": True}}, upsert=False)
        if request.method == 'POST':
            mongo.db.Sharedworkouts.insert_one(
                {
                    'user': session["user"],
                    "Date": share['Date'],
                    'Title': share['Title'],
                    'Routine': share['Routine'],
                    'Difficulty': share['Difficulty'],
                    'Savedby': saved
                })
        return redirect(url_for('workouts', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/Add-Goal/<username>", methods=["GET", "POST"])
def addgoal(username):
    # allows user to create a new goal
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        if request.method == 'POST':
            mongo.db.Goals.insert_one(
                {
                    'user': session["user"],
                    "Date": date.today().strftime("%d/%m/%Y"),
                    'Title': request.form['Title'],
                    'Details': request.form['Details'],
                    'Completed': "Incomplete"
                })
        return redirect(url_for('profile', username=username, files=file))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-goal/<username>_<goal_id>')
def editgoal(goal_id, username):
    # function that allows users to edit goals on main profile page
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        goal = list(mongo.db.Goals.find({"user": session["user"]}))
        return render_template('update-profile.html', username=username,
                               edit=edit, goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/updated-goal/<username>_<goal_id>', methods=['POST'])
def updategoal(goal_id, username):
    # function that updates a goal on the main profile page
    if username == session["user"]:
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        if not request.form['Details']:
            details = edit["Details"]
        else:
            details = request.form['Details']
        updates = {
                'user': session["user"],
                "Date": edit['Date'],
                'Title': request.form['Title'],
                'Details': details,
                'Completed': request.form['Completed']
            }
        mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
        return redirect(url_for('profile', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-goalcompleted/<username>_<goal_id>')
def editgoalcompleted(goal_id, username):
    # function that allows user to edit goal on completed page
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        goal = list(mongo.db.Goals.find({"user": session["user"],
                                        "Completed": "Complete"}))
        return render_template('update-profile-completed.html',
                               username=username, edit=edit,
                               goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/delete-goal/<username>_<goal_id>')
def deletegoal(goal_id, username):
    # function to delete goal on main profile page
    if username == session["user"]:
        mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
        return redirect(url_for('profile', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/updated-completedgoal/<username>_<goal_id>', methods=['POST'])
def updategoalcompleted(goal_id, username):
    # function to update data for a completed goal
    if username == session["user"]:
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        if not request.form['Details']:
            details = edit["Details"]
        else:
            details = request.form['Details']
        updates = {
                'user': session["user"],
                "Date": edit['Date'],
                'Title': request.form['Title'],
                'Details': details,
                'Completed': request.form['Completed']
            }
        mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
        return redirect(url_for('profilecompleted', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/delete-goalcompleted/<username>_<goal_id>')
def deletegoalcompleted(goal_id, username):
    # function to delete a goal on the completed page
    if username == session["user"]:
        mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
        return redirect(url_for('profilecompleted', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-goalinprogress/<username>_<goal_id>')
def editgoalinprogress(goal_id, username):
    # function to allow user to edit a goal in progress
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        goal = list(mongo.db.Goals.find({"user": session["user"],
                                        "Completed": "Incomplete"}))
        return render_template('update-profile-inprogress.html',
                               username=username, edit=edit,
                               goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/delete-goal-inprogress/<username>_<goal_id>')
def deletegoalinprogress(goal_id, username):
    # function to delete a goal from the inprogress page
    if username == session["user"]:
        mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
        return redirect(url_for('profileinprogress', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/updated-inprogressgoal/<username>_<goal_id>', methods=['POST'])
def updategoalinprogress(goal_id, username):
    # this is an function that updates the goal from the inprogress page
    if username == session["user"]:
        edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
        if not request.form['Details']:
            details = edit["Details"]
        else:
            details = request.form['Details']
        updates = {
                'user': session["user"],
                "Date": edit['Date'],
                'Title': request.form['Title'],
                'Details': details,
                'Completed': request.form['Completed']
            }
        mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
        return redirect(url_for('profileinprogress', username=username))
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-profilepicture/<username>')
def editprofilepicture(username):
    # this function allows user to edit profile picture on main profile page
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"]}))
        return render_template('update-profilepicture.html', username=username,
                               goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-profilepicture-completed/<username>')
def editprofilepicturecompleted(username):
    """ this function allows user to edit profile picture
    while on the complete goals page """
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"],
                                        "Completed": "Complete"}))
        return render_template('update-profilepicture-completed.html',
                               username=username, goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route('/edit-profilepicture-inprogress/<username>')
def editprofilepictureinprogress(username):
    """ this function allows user to edit profile picture
    while on the inprogress goals page """
    if username == session["user"]:
        file = list(mongo.db.files.find({"id": session["user"]}))
        goal = list(mongo.db.Goals.find({"user": session["user"],
                                        "Completed": "Incomplete"}))
        return render_template('update-profilepicture-inprogress.html',
                               username=username, goals=goal, files=file)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/search-workouts/<username>", methods=["GET", "POST"])
def search(username):
    # function for search bar on workout page
    if username == session["user"]:
        query = request.form.get("query")
        workout = list(mongo.db.Workouts.find({"$text": {"$search": query}}))
        file = list(mongo.db.files.find({"id": session["user"]}))
        return render_template("workouts.html", username=username,
                               files=file, workouts=workout)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/search-sharedworkouts/<username>", methods=["GET", "POST"])
def sharedsearch(username):
    # function for search bar on workout page
    if username == session["user"]:
        query = request.form.get("query")
        sharedworkout = list(mongo.db.Sharedworkouts.find({"$text":
                             {"$search": query}}))
        file = list(mongo.db.files.find({"id": session["user"]}))
        return render_template("sharedworkouts.html", username=username,
                               files=file, workouts=sharedworkout)
    flash("You need to log in")
    return redirect(url_for("login"))


@app.route("/search-savedsharedworkouts/<username>", methods=["GET", "POST"])
def savedsearch(username):
    # function for search bar on workout page
    if username == session["user"]:
        query = request.form.get("query")
        sharedworkout = list(mongo.db.Sharedworkouts.find({"$text":
                             {"$search": query}}))
        file = list(mongo.db.files.find())
        return render_template("savedsharedworkouts.html", username=username,
                               files=file, workouts=sharedworkout)
    flash("You need to log in")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
