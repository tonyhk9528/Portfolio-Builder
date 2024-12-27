from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from datetime import timedelta
from sqlalchemy import text
import json

from portfolio import app, db
from portfolio.models import *



@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #validate submission

        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        role = request.form.get('role')
        email = request.form.get('email')
        headline = request.form.get('headline')

        sql = """
                INSERT INTO users 
                (username, password_hash, first_name, last_name, email, role, headline) 
                VALUES 
                (:username, :password_hash, :first_name, :last_name, :email, :role, :headline)
            """
        sql_q = text(sql)

        #Add users
        db.session.execute(
            sql_q,
            {
            "username": username,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "headline": headline
                }
        )

        db.session.commit()

        #get id
        sql_id = "SELECT id, username, password_hash FROM users WHERE username = :username"
        sql_id = text(sql_id)
        user = db.engine.connect().execute(sql_id, {'username': username}).fetchone()
        user_id = user.id

        #initialise about
        sql_about = "INSERT INTO about (user_id, about_me) VALUES (:user_id, :about_me)"
        db.session.execute(text(sql_about), {
            "user_id": user_id,                
            "about_me": "Write a couple-paragraphs-long summary about yourself. It can be about your upbring, passion, past experiences or even hobbies. This is your chance to give a good first impression and showcase your personality!",
            })

        #initialise experience

        #initialise education

        #initialise skills

        #initialise projects



        db.session.commit()
        flash("Account created successfully!")
        return redirect( url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember-me')

        sql = "SELECT id, username, password_hash FROM users WHERE username = :username"
        sql = text(sql)
        user = db.engine.connect().execute(sql, {'username': username}).fetchone()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            if remember_me == 'on':
                session.permanent = True
            else:
                session.permanent = False
            
            return redirect(url_for('dashboard'))
        
        else:
            flash('Invalid credentials. Please try again.', 'error')
           
    if "user_id" in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session["user_id"]

    if request.method == 'POST':
        new_first_name = request.form.get('first-name')
        new_last_name = request.form.get('last-name')
        new_role = request.form.get('role')
        new_email = request.form.get('email')
        new_headline = request.form.get('headline')
        

        sql = """
                UPDATE users 
                SET  
                first_name= :first_name, last_name = :last_name, email = :email, role = :role, headline = :headline
                WHERE id = :id
            """
        sql_q = text(sql)

        #Update users
        db.session.execute(
            sql_q,
            {
            "first_name": new_first_name,
            "last_name": new_last_name,
            "email": new_email,
            "role": new_role,
            "headline": new_headline,
            "id": user_id
                }
        )
        db.session.commit()
        flash("Information updated successfully!")
        return redirect( url_for('dashboard'))




    if "user_id" in session:
        
        sql = text("SELECT * FROM users WHERE id = :id")
        user = db.engine.connect().execute(sql, {'id': user_id}).fetchone()
        return render_template('dashboard.html', user=user)

    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/about', methods = ['GET', 'POST'])
def about():
    user_id = session["user_id"]
    username = session["username"]
    

    sql = "SELECT about_me FROM about WHERE user_id = :user_id"
    sql = text(sql)
    user_about = db.engine.connect().execute(sql, {'user_id': user_id}).fetchone()

    if user_about:  
        about = user_about.about_me
    else:
        about = ""


    if request.method == 'POST':
        new_about = request.form.get('about')
        sql = """
                UPDATE about 
                SET  
                about_me= :about_me
                WHERE user_id = :user_id
            """
        sql_q = text(sql)

        #Update users
        db.session.execute(
            sql_q,
            {
            "about_me": new_about,
            "user_id": user_id
                }
        )
        db.session.commit()
        flash("Information updated successfully!")
        return redirect( url_for('about'))




    return render_template("about.html", username=username, user_id=user_id, about=about)
