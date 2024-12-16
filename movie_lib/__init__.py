from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from sqlalchemy.orm import declarative_base


app = Flask(__name__, static_folder="static")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'movie_library.db')
# initialize the app with the extension
db = SQLAlchemy(app)

Base = declarative_base()
Base.query = db.session.query_property()


import movie_lib.routes