import os
import json
import uuid
from flask import Flask, render_template, session, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
from collections import OrderedDict
from datetime import datetime as date
import bcrypt
if path.exists("env.py"):
    import env

app = Flask(__name__)

# Defining variables database and MongoDB url
app.config["MONGO_DBNAME"] = os.getenv('MONGO_DBNAME')
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)
# The initial page that is loaded upon first accessing the application

@app.route("/")
def hello():
    return "hello"

