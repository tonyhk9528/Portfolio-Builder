from datetime import datetime
import re
import os

from flask import render_template, redirect, url_for, request, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


from portfolio import app, db

# Banned passwords list 
# The National Cyber Security Centre
# Accessed 06-01-2025
# https://www.ncsc.gov.uk/static-assets/documents/PwnedPasswordsTop100k.txt
basedir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(basedir, 'static/PwnedPasswordsTop100k.txt'), encoding='utf-8') as fin:
    banned_passwords = set(line.strip() for line in fin)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        username = request.form.get('username').lower().strip()
        password = request.form.get('password')
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        first_name = request.form.get('first-name').strip()
        last_name = request.form.get('last-name').strip()
        role = request.form.get('role').strip()
        email = request.form.get('email').strip()
        headline = request.form.get('headline').strip()

        #validate username, password, and email 
        if not 3 <= len(username) <= 20:
            flash("Username must be 3-20 characters long.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")
                
        if password in banned_passwords or password == username:
            flash("Please pick a less common password.", "danger")
            return render_template("register.html")
        
        #validate null input
        if not username or not password or not first_name or not last_name or not role or not email or not headline:
            flash("Registration failed due to empty field.", "danger")
            return render_template("register.html")


        #Regex to check for email
        #taken from StackOverflow
        #accessed 05-01-2025
        #https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            flash("Invalid email address.", "danger")
            return render_template("register.html")
        

        sql = """
                INSERT INTO users 
                (username, password_hash, first_name, last_name, email, role, headline) 
                VALUES 
                (:username, :password_hash, :first_name, :last_name, :email, :role, :headline)
            """
        sql_q = text(sql)

        #Catch UNIQUE constraint in db
        try:
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

        except IntegrityError:
            db.session.rollback()
            flash("Registration failed due to unexpected error.", "danger")
            return render_template('register.html')

        #get id
        sql_id = "SELECT id, username, password_hash FROM users WHERE username = :username"
        sql_id = text(sql_id)
        user = db.engine.connect().execute(sql_id, {'username': username}).fetchone()
        user_id = user.id

        #initialise About
        sql_about = "INSERT INTO about (user_id, about_me) VALUES (:user_id, :about_me)"
        db.session.execute(text(sql_about), {
            "user_id": user_id,                
            "about_me": """
                Write a couple-paragraphs-long summary about yourself. 
                It can be about your upbring, passion, past experiences or even hobbies. 
                This is your chance to give a good first impression and showcase your personality!
            """
        })

        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect( url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower().strip()
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
            flash('Invalid credentials. Please try again.', 'danger')
           
    if "user_id" in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get("user_id"):
        flash("Please login first.", 'warning')
        return redirect(url_for('login'))

    user_id = session["user_id"]

    if request.method == 'POST':
        new_first_name = request.form.get('first-name')
        new_last_name = request.form.get('last-name')
        new_role = request.form.get('role')
        new_email = request.form.get('email')
        new_headline = request.form.get('headline')
        new_resume = request.files.get("resume")

        #validate null input
        if not new_first_name or not new_last_name or not new_role or not new_email or not new_headline:
            flash("Update failed due to empty field(s).", "danger")
            return redirect(url_for('dashboard'))

        #validate email
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", new_email):
            flash("Invalid email address.", "danger")
            return redirect(url_for('dashboard'))

        #Get existing resume file name
        sql = "SELECT resume FROM users WHERE id = :id"
        sql_q = text(sql)
        result = db.engine.connect().execute(sql_q, {'id':user_id}).fetchone()
        resume = result.resume

        if new_resume:
            #validate file type
            if new_resume.filename[-4:].strip().lower() != '.pdf':
                flash("Please upload your resume in pdf format.", "danger")
                return redirect(url_for('dashboard'))


            #Save file
            new_resume_filename = f"{user_id}_{secure_filename(new_resume.filename)}" 
            new_resume.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads', new_resume_filename))

        else:
            new_resume_filename = resume

        

        sql = """
                UPDATE users 
                SET  
                first_name= :first_name, last_name = :last_name, email = :email, role = :role, headline = :headline, resume = :resume
                WHERE id = :id
            """
        sql_q = text(sql)

        #Update users
        try:
            db.session.execute(
                sql_q,
                {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "email": new_email,
                "role": new_role,
                "headline": new_headline,
                "resume": new_resume_filename,
                "id": user_id
                    }
            )
            db.session.commit()
            flash("Information updated successfully!", 'success')
            return redirect( url_for('dashboard'))

        except IntegrityError:
            db.session.rollback()
            flash("Update failed due to unexpected error.", 'danger')



    sql = text("SELECT * FROM users WHERE id = :id")
    user = db.engine.connect().execute(sql, {'id': user_id}).fetchone()
    return render_template('dashboard.html', user=user)



@app.route('/logout', methods = ['POST'])
def logout():
    if request.method == 'POST':
        if not session.get("user_id"):
            return redirect(url_for('login'))
        else:
            session.clear()
            flash("You have been logged out.", "success")
            return redirect(url_for('login'))



@app.route('/about', methods = ['GET', 'POST'])
def about():
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    user_id = session["user_id"]
    username = session["username"]
    

    sql = "SELECT about_me FROM about WHERE user_id = :user_id"
    sql = text(sql)
    user_about = db.engine.connect().execute(sql, {'user_id': user_id}).fetchone()

    about = user_about.about_me


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
        flash("About updated successfully!", "success")
        return redirect( url_for('about'))


    return render_template("about.html", username=username, user_id=user_id, about=about)


@app.route('/skills', methods = ['GET', 'POST'])
def skills():
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    user_id = session["user_id"]
    username = session["username"]
    icons = [
        "Analytics", "Cloud", "Coding", "Communication", "CSS", "Database", 
        "HTML", "JavaScript", "Leadership", "Project Management", "Public Speaking", 
        "Sale", "Science", "Teamwork", "Translation", "Writing"
    ]

    if request.method == "POST":
        skill_name = request.form.get("skill_name")
        skill_content = request.form.get("skill_content")
        skill_icon = request.form.get("skill_icon")

        #Ensure name is not null
        if not skill_name:
            flash("Please enter skill name", "danger")
            return redirect( url_for('skills'))


        #validate skill_icon
        if skill_icon not in icons:
            flash("Unsupported icon submitted", "danger")
            return redirect( url_for('skills'))

        sql = """
                INSERT INTO skills 
                (skill_name, skill_content, skill_icon, user_id) 
                VALUES 
                (:skill_name, :skill_content, :skill_icon, :user_id)
            """
        sql_q = text(sql)

        #Add skill
        db.session.execute(
            sql_q,
            {
            "skill_name": skill_name,
            "skill_content": skill_content,
            "skill_icon": skill_icon,
            "user_id": user_id
                }
        )

        db.session.commit()
        return redirect(url_for('skills'))


    sql = "SELECT * FROM skills WHERE user_id = :user_id"
    sql = text(sql)
    user_skills = db.engine.connect().execute(sql, {'user_id': user_id}).fetchall()

    return render_template("skills.html", username=username, icons=icons, user_skills=user_skills)


@app.route('/skills/edit/<int:id>', methods = ['GET', 'POST'])
def edit_skill(id):
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))
    
    user_id = session["user_id"]
    username = session["username"]
    icons = [
        "Analytics", "Cloud", "Coding", "Communication", "CSS", "Database", 
        "HTML", "JavaScript", "Leadership", "Project Management", "Public Speaking", 
        "Sale", "Science", "Teamwork", "Translation", "Writing"
    ]

    #validate ownership
    sql_validate = "SELECT user_id FROM skills WHERE skill_id = :skill_id"
    sql_validate_q = text(sql_validate)
    result = db.engine.connect().execute(sql_validate_q, {'skill_id':id}).fetchone()
    if not result:
        abort(404, description="Item not found.")
        return redirect(url_for('skills'))


    if result.user_id != user_id:
        flash("Invalid permission.", "danger")
        return redirect(url_for('skills'))
    

    if request.method == 'POST':
        new_skill_name = request.form.get('skill_name')
        new_skill_icon = request.form.get('skill_icon')
        new_skill_content = request.form.get('skill_content')
    
        #Ensure name is not null
        if not new_skill_name:
            flash("Please enter skill name", "danger")
            return redirect(url_for('skills'))


        #validate skill_icon
        if new_skill_icon not in icons:
            flash("Unsupported icon submitted", "danger")
            return redirect(url_for('skills'))

        

        sql = """
                UPDATE skills 
                SET  
                skill_name= :skill_name, skill_icon = :skill_icon, skill_content = :skill_content
                WHERE user_id = :user_id AND skill_id = :skill_id
            """
        sql_q = text(sql)


        #Update skill
        db.session.execute(
            sql_q,
            {
            "skill_name": new_skill_name,
            "skill_icon": new_skill_icon,
            "skill_content": new_skill_content,
            "user_id": user_id,
            "skill_id": id
                }
        )
        db.session.commit()
        flash("Skill updated successfully!", "success")
        return redirect( url_for('skills'))


    #Query for current skill
    sql = "SELECT * FROM skills WHERE user_id = :user_id AND skill_id = :skill_id"
    sql_q = text(sql)
    user_skill = db.engine.connect().execute(sql_q, {'user_id':user_id, 'skill_id':id}).fetchone()


    
    return render_template("edit_skill.html", user_skill=user_skill, icons=icons)



@app.route('/skills/delete/<int:id>', methods = ['POST'])
def delete_skill(id):
    if request.method == 'POST':
        if not session.get("user_id"):
            flash("Please login first", "warning")
            return redirect(url_for('login'))
        
        user_id = session["user_id"]
        username = session["username"]

        #validate ownership
        sql_validate = "SELECT user_id FROM skills WHERE skill_id = :skill_id"
        sql_validate_q = text(sql_validate)
        result = db.engine.connect().execute(sql_validate_q, {'skill_id':id}).fetchone()
        if result.user_id != user_id:
            flash('Invalid permission', 'danger')
            return redirect(url_for('skills'))


        #Delete skill
        sql = """
                DELETE FROM skills 
                WHERE user_id = :user_id AND skill_id = :skill_id
            """
        sql_q = text(sql)

        
        db.session.execute(
            sql_q,
            {
            "user_id": user_id,
            "skill_id": id
                }
        )

        db.session.commit()
        return redirect(url_for('skills'))


@app.route('/experience', methods = ['GET', 'POST'])
def experience():
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    user_id = session["user_id"]
    username = session["username"]

    if request.method == "POST":
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        employer = request.form.get('employer')
        role = request.form.get('role')
        description = request.form.get('description')
        tags = request.form.get('exp-tag')

        #validate input
        if not start_date or not end_date or not employer or not role or not description:
            flash("Updated failed due to empty field(s).", "danger")
            return redirect(url_for('experience'))

        if not re.match(r'^([0-9]{4})-(1[0-2]|0[1-9])$', start_date):
            flash("Invalid start date.", "danger")
            return redirect(url_for('experience'))
        
        if not re.match(r'^([0-9]{4})-(1[0-2]|0[1-9])$', end_date) and end_date != 'CURRENT':
            flash("Invalid end date.", "danger")
            return redirect(url_for('experience'))

        
        sql = """
                INSERT INTO experience 
                (user_id, start_date, end_date, employer, role, description, tags) 
                VALUES 
                (:user_id, :start_date, :end_date, :employer, :role, :description, :tags)
            """
        sql_q = text(sql)

        #Add experience
        db.session.execute(
            sql_q,
            {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "employer": employer,
            "role": role,
            "description": description,
            "tags": tags
                }
        )

        db.session.commit()
        return redirect(url_for('experience'))


    sql = "SELECT * FROM experience WHERE user_id = :user_id ORDER BY end_date DESC, start_date DESC"
    sql = text(sql)
    result = db.engine.connect().execute(sql, {'user_id': user_id}).fetchall()

    if result:
        user_experience_list = [
            {
                "experience_id": row.experience_id,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "employer": row.employer,
                "role": row.role,
                "description": row.description,
                "tags": row.tags.split(',') if row.tags else [],
                "start_date_formatted": datetime.strptime(row.start_date, "%Y-%m").strftime("%b-%Y").upper(),
                "end_date_formatted": datetime.strptime(row.end_date, "%Y-%m").strftime("%b-%Y").upper() if row.end_date != 'CURRENT' else row.end_date,
            }
            for row in result
        ]    
    else:
        user_experience_list = None

    return render_template("experience.html", username=username, user_experience_list=user_experience_list)




@app.route('/experience/edit/<int:id>', methods = ['GET', 'POST'])
def edit_experience(id):
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))
    
    user_id = session["user_id"]
    username = session["username"]

    #validate ownership
    sql_validate = "SELECT user_id FROM experience WHERE experience_id = :experience_id"
    sql_validate_q = text(sql_validate)
    result = db.engine.connect().execute(sql_validate_q, {'experience_id':id}).fetchone()
    if not result:
        abort(404, description="Item not found.")
        return redirect(url_for('experience'))

    if result.user_id != user_id:
        flash('Invalid permission', 'danger')
        return redirect(url_for('experience'))


    if request.method == 'POST':
        new_start_date = request.form.get('start_date')
        new_end_date = request.form.get('end_date')
        new_employer = request.form.get('employer')
        new_role = request.form.get('role')
        new_description = request.form.get('description')
        new_tags = request.form.get('exp-tag')

        #validate input
        if not new_start_date or not new_end_date or not new_employer or not new_role or not new_description:
            flash("Updated failed due to empty field detected.", "danger")
            return redirect(url_for('experience'))

        if not re.match(r'^([0-9]{4})-(1[0-2]|0[1-9])$', new_start_date):
            flash("Invalid start date.", "danger")
            return redirect(url_for('experience'))
        
        if not re.match(r'^([0-9]{4})-(1[0-2]|0[1-9])$', new_end_date) and new_end_date != 'CURRENT':
            flash("Invalid end date.", "danger")
            return redirect(url_for('experience'))


        

        sql = """
                UPDATE experience 
                SET  
                start_date= :start_date, end_date = :end_date, employer = :employer, role = :role, description = :description, tags = :tags
                WHERE user_id = :user_id AND experience_id = :experience_id
            """
        sql_q = text(sql)

        #Update experience
        db.session.execute(
            sql_q,
            {
            "start_date": new_start_date,
            "end_date": new_end_date,
            "employer": new_employer,
            "role": new_role,
            "description": new_description,
            "tags": new_tags,
            "user_id": user_id,
            "experience_id": id
                }
        )
        db.session.commit()
        flash("Experience updated successfully!", "success")
        return redirect( url_for('experience'))


    #Query for current experience
    sql = "SELECT * FROM experience WHERE user_id = :user_id AND experience_id = :experience_id"
    sql_q = text(sql)
    user_experience = db.engine.connect().execute(sql_q, {'user_id':user_id, 'experience_id':id}).fetchone()

    
    return render_template("edit_experience.html", user_experience=user_experience)


@app.route('/experience/delete/<int:id>', methods=['POST'])
def delete_experience(id):
    if request.method == 'POST':
        if not session.get("user_id"):
            flash("Please login first", "warning")
            return redirect(url_for('login'))
        
        user_id = session["user_id"]
        username = session["username"]

        #validate ownership
        sql_validate = "SELECT user_id FROM experience WHERE experience_id = :experience_id"
        sql_validate_q = text(sql_validate)
        result = db.engine.connect().execute(sql_validate_q, {'experience_id':id}).fetchone()
        if result.user_id != user_id:
            flash("Invalid permission", "danger")
            return redirect(url_for('experience'))


        #Delete skill
        sql = """
                DELETE FROM experience 
                WHERE user_id = :user_id AND experience_id = :experience_id
            """
        sql_q = text(sql)

        
        db.session.execute(
            sql_q,
            {
            "user_id": user_id,
            "experience_id": id
                }
        )

        db.session.commit()
        return redirect(url_for('experience'))


@app.route('/projects', methods = ['GET', 'POST'])
def projects():
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    user_id = session["user_id"]
    username = session["username"]

    if request.method == "POST":
        project_name = request.form.get("project-name")
        project_description = request.form.get("project-description")
        project_screenshot = request.files.get("project-screenshot")
        project_url = request.form.get("project-url")
        project_tags = request.form.get("project-tags")
        project_order = request.form.get("project-order")

        #validate input
        if not project_name or not project_description:
            flash("Update failed due to empty field(s) detected.", "danger")
            return redirect(url_for('projects'))

        if project_screenshot:
            #validate file type
            if project_screenshot.filename[-4:].strip().lower() not in ALLOWED_EXTENSIONS and project_screenshot.filename[-5:].strip().lower() not in ALLOWED_EXTENSIONS:
                flash("Update failed due to unsupported image type.", "danger")
                return redirect(url_for('projects'))

            #Save file
            project_screenshot_filename = f"{str(user_id)}_{secure_filename(project_screenshot.filename)}"
            project_screenshot.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads', project_screenshot_filename))

        else:
            project_screenshot_filename = "project-placeholder.jpg"

        #Order handle
        project_order = int(project_order) if project_order and project_order.isdigit() and int(project_order) > 0 else 1

        #Add project
        sql = """
                INSERT INTO projects 
                (user_id, project_name, project_description, project_screenshot, project_url, tags, sort_order) 
                VALUES 
                (:user_id, :project_name, :project_description, :project_screenshot, :project_url, :tags, :sort_order)
            """
        sql_q = text(sql)

        db.session.execute(
            sql_q,
            {
            "user_id": user_id,
            "project_name": project_name,
            "project_description": project_description,
            "project_screenshot": project_screenshot_filename,
            "project_url": project_url,
            "tags": project_tags,
            "sort_order": project_order
                }
        )

        db.session.commit()
        return redirect(url_for('projects'))



    sql = "SELECT * FROM projects WHERE user_id = :user_id ORDER BY sort_order, project_id"
    sql_q = text(sql)
    user_projects = db.engine.connect().execute(sql_q, {'user_id': user_id}).fetchall()

    

    return render_template("projects.html", username=username, user_projects=user_projects)


@app.route('/projects/edit/<int:id>', methods = ['GET', 'POST'])
def edit_project(id):
    if not session.get("user_id"):
        flash("Please login first", "warning")
        return redirect(url_for('login'))
    
    user_id = session["user_id"]
    username = session["username"]

    #validate ownership
    sql_validate = "SELECT user_id, project_screenshot FROM projects WHERE project_id = :project_id"
    sql_validate_q = text(sql_validate)
    result = db.engine.connect().execute(sql_validate_q, {'project_id':id}).fetchone()
    if not result:
        abort(404, description="Item not found.")
        return redirect(url_for('projects'))

    if result.user_id != user_id:
        flash("Invalid permission", "danger")
        return redirect(url_for('projects'))

    project_screenshot = result.project_screenshot

    if request.method == 'POST':
        new_project_name = request.form.get("project-name")
        new_project_description = request.form.get("project-description")
        new_project_screenshot = request.files.get("project-screenshot")
        new_project_url = request.form.get("project-url")
        new_project_tags = request.form.get("project-tags")
        new_project_order = request.form.get("project-order")

        #validate input
        if not new_project_name or not new_project_description:
            flash("Update failed due to empty field(s) detected.", "danger")
            return redirect(url_for('projects'))


        if new_project_screenshot:
            #Validate file type:
            if new_project_screenshot.filename[-4:].strip().lower() not in ALLOWED_EXTENSIONS and new_project_screenshot.filename[-5:].strip().lower() not in ALLOWED_EXTENSIONS:
                flash("Update failed due to unsupported image type.", "danger")
                return redirect(url_for('projects'))

            #Save file
            new_project_screenshot_filename = f"{str(user_id)}_{secure_filename(new_project_screenshot.filename)}"
            new_project_screenshot.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads', new_project_screenshot_filename))

        else:
            new_project_screenshot_filename = project_screenshot

        #Order handle
        new_project_order = int(new_project_order) if new_project_order and new_project_order.isdigit() and int(new_project_order) > 0 else 1

        

        sql = """
                UPDATE projects 
                SET  
                project_name= :project_name, project_description = :project_description, project_screenshot = :project_screenshot, project_url = :project_url, tags = :tags, sort_order = :sort_order
                WHERE user_id = :user_id AND project_id = :project_id
            """
        sql_q = text(sql)

        #Update experience
        db.session.execute(
            sql_q,
            {
            "project_name": new_project_name,
            "project_description": new_project_description,
            "project_screenshot": new_project_screenshot_filename,
            "project_url": new_project_url,
            "tags": new_project_tags,
            "sort_order": new_project_order ,
            "user_id": user_id,
            "project_id": id
                }
        )
        db.session.commit()
        flash("Project updated successfully!", "success")
        return redirect( url_for('projects'))


    #Query for current experience
    sql = "SELECT * FROM projects WHERE user_id = :user_id AND project_id = :project_id"
    sql_q = text(sql)
    user_project = db.engine.connect().execute(sql_q, {'user_id':user_id, 'project_id':id}).fetchone()

    
    return render_template("edit_project.html", user_project=user_project)


@app.route('/projects/delete/<int:id>', methods = ['POST'])
def delete_project(id):
    if request.method == 'POST':
        if not session.get("user_id"):
            flash("Please login first", "warning")
            return redirect(url_for('login'))
        
        user_id = session["user_id"]
        username = session["username"]

        #validate ownership
        sql_validate = "SELECT user_id FROM projects WHERE project_id = :project_id"
        sql_validate_q = text(sql_validate)
        result = db.engine.connect().execute(sql_validate_q, {'project_id':id}).fetchone()
        if result.user_id != user_id:
            flash("Invalid permission", "danger")
            return redirect(url_for('projects'))


        #Delete skill
        sql = """
                DELETE FROM projects 
                WHERE user_id = :user_id AND project_id = :project_id
            """
        sql_q = text(sql)

        
        db.session.execute(
            sql_q,
            {
            "user_id": user_id,
            "project_id": id
                }
        )

        db.session.commit()
        return redirect(url_for('projects'))


@app.route('/portfolio/<username>')
def portfolio(username):

    #Get user's info and about
    sql = "SELECT * FROM users JOIN about ON users.id = about.user_id WHERE users.username = :username"
    sql_q = text(sql)
    with db.engine.connect() as connection:
        user = connection.execute(sql_q, {'username': username}).fetchone()

    #incorrect path name handling
    if not user:
        abort(404, description="User not found")

    user_id = user.id

    #Get skills
    sql = "SELECT * FROM skills WHERE user_id = :user_id"
    sql_q = text(sql)
    with db.engine.connect() as connection:
        user_skills = connection.execute(sql_q, {'user_id': user_id}).fetchall()


    #Get experience
    sql = "SELECT * FROM experience WHERE user_id = :user_id"
    sql_q = text(sql)
    with db.engine.connect() as connection:
        result = connection.execute(sql_q, {'user_id': user_id}).fetchall()

    if result:
        user_experience_list = [
            {
                "experience_id": row.experience_id,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "employer": row.employer,
                "role": row.role,
                "description": row.description,
                "tags": row.tags.split(',') if row.tags else [],
                "start_date_formatted": datetime.strptime(row.start_date, "%Y-%m").strftime("%b-%Y").upper(),
                "end_date_formatted": datetime.strptime(row.end_date, "%Y-%m").strftime("%b-%Y").upper() if row.end_date != 'CURRENT' else row.end_date,
            }
            for row in result
        ]    
    else:
        user_experience_list = None


    #Get projects
    sql = "SELECT * FROM projects WHERE user_id = :user_id ORDER BY sort_order, project_id"
    sql_q = text(sql)
    with db.engine.connect() as connection:
        user_projects = connection.execute(sql_q, {'user_id': user_id}).fetchall()



    return render_template('portfolio.html', user=user, user_skills=user_skills, user_experience_list=user_experience_list, user_projects=user_projects)
