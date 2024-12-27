from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta

from sqlalchemy.orm import declarative_base


app = Flask(__name__, static_folder="static")
app.secret_key = 'thisisasecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)



basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'portfolio.db')
# initialize the app with the extension
db = SQLAlchemy(app)

Base = declarative_base()
Base.query = db.session.query_property()


import portfolio.routes