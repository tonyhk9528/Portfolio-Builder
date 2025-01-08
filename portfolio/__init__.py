from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os
from datetime import timedelta

from sqlalchemy.orm import declarative_base


app = Flask(__name__, static_folder="static")
app.secret_key = '5p283xcecw1c' #random string gnerated using https://www.random.org/strings/
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
csrf = CSRFProtect(app)



basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'portfolio.db')
# initialize the app with the extension
db = SQLAlchemy(app)

Base = declarative_base()
Base.query = db.session.query_property()


import portfolio.routes