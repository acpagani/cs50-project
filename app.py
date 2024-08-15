import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from datetime import datetime

# Create flask application
app = Flask(__name__)

# Session to be filesystem not cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Initialize SQL database by cs50 library
db = SQL("sqlite:///buildata.db")


# Ensure user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Rendering the home page, with user's name on it
@app.route("/")
@login_required
def index():
    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])
    return render_template("home_page.html", name=username[0])


# Worker's table management
@app.route("/mng_workers")
@login_required
def mng_workers():
    data_workers = db.execute("SELECT * FROM workers WHERE user_id=?", session["user_id"])
    return render_template("mng_workers.html", data_workers=data_workers)


# Registering user in platform
@app.route("/signin", methods=["GET", "POST"])
def signin():

    # In case of submitting sign in form
    if request.method == "POST":

        # Gets all users usernames
        data_users = db.execute("SELECT * FROM users")

        # Getting user input from .html
        data_input = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "password_confirmation": request.form.get("password_confirm")
        }

        # Ensure all inputs are fulfilled
        for data in data_input.values():
            if data == '':
                return render_template("error.html", code="401", error_message="Must provide all inputs")

        # Password and confirmation don't match
        if data_input["password"] != data_input["password_confirmation"]:
            return render_template("error.html", code="401", error_message="Passwords don't match")

        # Checking if the username is already taken by another user
        is_already_signed = False
        for data in data_users:
            if data["username"] == data_input["username"]:
                is_already_signed = True

        # If the username is not being used
        if not is_already_signed:

            # Hash the password (cryptography)
            hash_password = generate_password_hash(data_input["password"])

            # Insert new user data in database
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", data_input["username"], hash_password)

            # Set session ID to be user ID
            user_id = db.execute("SELECT id FROM users WHERE username=?", data_input["username"])
            session["user_id"] = user_id[0]["id"]

            # Automatic login
            flash(f"Welcome to BuilData user {data_input['username']}!")
            return redirect("/")

        # Username already taken
        else:
            return render_template("error.html", code="401", error_message="Username already taken")

    # In case of just opening the section
    else:
        # If user returns to sign page after signing in
        session.clear()

        return render_template("signin.html")


# Logging user
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Just being sure the session is clear
        session.clear()

        # Get user input from .html
        data_input = {
            "username": request.form.get("username"),
            "password": request.form.get("password")
        }

        # Catch username data from database
        data_users = db.execute("SELECT * FROM users WHERE username=?", data_input["username"])

        # Ensure all inputs are fulfilled
        for data in data_input.values():
            if data == '':
                return render_template("error.html", code="401", error_message="Must fill all inputs")

        # Username input does not exist
        if len(data_users) != 1:
            return render_template("error.html", code="401", error_message="Username does not exist")

        # Password from input and from database don't match
        elif not check_password_hash(data_users[0]["password"], data_input["password"]):
            return render_template("error.html", code="401", error_message="Incorrect password")

        # Set session ID to be user ID
        session["user_id"] = data_users[0]["id"]

        # Get into page
        flash(f"Welcome back to BuilData user {data_input['username']}!")
        return redirect("/")

    # In case of just opening the section
    else:
        # If user returns to login page after logging in
        session.clear()

        return render_template("login.html")


# Register a new construction
@app.route("/new_constr", methods=["GET", "POST"])
@login_required
def new_constr():
    if request.method == "POST":
        # Catch all user input
        data_input = {
            "constr-name": request.form.get("constr-name"),
            "client-name": request.form.get("client-name"),
            "client-address": request.form.get("client-address"),
            "start-date": request.form.get("start-date"),
            "end-date": request.form.get("end-date"),
            "selected-workers": request.form.get("selected-workers")
        }

        # Check if all data was provided
        for data in data_input.values():
            if data == '':
                return render_template("error.html", code="401", error_message="Must provide all construction data")

        # Turn selected-workers data (csv) into a list
        selected_workers = data_input["selected-workers"].split(",")
        # Remove duplicates
        selected_workers = list(dict.fromkeys(selected_workers))

        # Insert construction data into database
        db.execute("INSERT INTO constructions (user_id, construction_name, client, address, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], data_input["constr-name"], data_input["client-name"], data_input["client-address"], data_input["start-date"], data_input["end-date"])

        # Select construction id previously added
        construction_id = db.execute("SELECT id FROM constructions WHERE user_id=? AND client=? AND construction_name=?",
                                     session["user_id"], data_input["client-name"], data_input["constr-name"])

        # For each worker in the workers' list
        for worker in selected_workers:

            # In case of blank inputs
            if worker == '':
                continue
            # Search selected worker's id from workers' table
            worker_id = db.execute("SELECT id FROM workers WHERE user_id=? AND name=?", session["user_id"], worker)

            # Insert catched data into database
            db.execute("INSERT INTO selected_workers (construction_id, worker_id) VALUES (?, ?)",
                       construction_id[0]["id"], worker_id[0]["id"])

        # Redirect user to construction's manager page
        flash("Construction added successfully!")
        return redirect("/mng_constr")
    else:
        # Display new contruction interface with all workers availables in each select
        workers_data = db.execute("SELECT * FROM workers WHERE user_id=?", session["user_id"])
        return render_template("new_constr.html", workers=workers_data)


# Manage and show constructions created
@app.route("/mng_constr")
@login_required
def mng_constr():
    constructions = db.execute("SELECT * FROM constructions WHERE user_id=?", session["user_id"])
    return render_template("mng_constr.html", constructions=constructions)


# Retrive a specific construction's information
@app.route("/constr_info", methods=["GET", "POST"])
@login_required
def constr_info():
    # In case of user posting a contruction's update
    if request.method == "POST":

        # Keep construction's id selected
        construction_id = session["constr_id"]
        data_input = {
            "title": request.form.get("post-title"),
            "description": request.form.get("post-description"),
            "photo": request.files.getlist("photos-uploaded")
        }

        # Record the exact time that the post was posted
        date_time = datetime.now()
        # Format the posting date
        post_date = f"{date_time.strftime('%x')} | {date_time.strftime('%X')}"

        # Insert into database
        db.execute("INSERT INTO posts (user_id, construction_id, datetime, title, description) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], construction_id, post_date, data_input["title"], data_input["description"])

        # Checking if at least one photo was uploaded
        if data_input["photo"] is not None and len(data_input["photo"]) != 0 and data_input["photo"][0].filename != "":

            # In case of user uploading multiple photos for one post, we need to save them individually
            for photo in data_input["photo"]:
                # Catch the post id just submitted
                new_post_id = db.execute("SELECT id FROM posts WHERE datetime=?", post_date)

                # Folders paths
                user = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"]
                client = db.execute("SELECT client FROM constructions WHERE id=?", construction_id)[0]["client"]

                photo_path = f"static/images/{user}/{client}/"

                if not os.path.exists(photo_path):
                    os.makedirs(photo_path)

                # Saving the photo
                photo_path += photo.filename
                photo.save(photo_path)

                # Inserting photo into database (related with it's post)
                db.execute("INSERT INTO photos (post_id, photo) VALUES (?, ?)", new_post_id[0]["id"], photo_path)

        # Redirect user to the same page, but in a get request, so the page will be reloaded with actual info
        flash(f"Post uploaded successfully!")
        return redirect("/constr_info")
    else:
        # Get the construction's id from the mng_constr screen
        construction_id = request.args.get("id")
        
        if construction_id:
            session["constr_id"] = construction_id

        # Data that will be displayed in screen
        construction_data = db.execute("SELECT * FROM constructions WHERE id=?", session["constr_id"])
        posts = db.execute("SELECT * FROM posts WHERE construction_id=? ORDER BY id DESC", session["constr_id"])
        username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])
        photos = db.execute("SELECT * FROM photos")

        # Formatting line breaks
        for p in range(len(posts)):
            posts[p]["description"] = posts[p]["description"].replace("\r\n", "<br>")

        # Staff team
        selected_workers = db.execute("""SELECT * FROM workers
                           JOIN selected_workers ON workers.id = worker_id
                           JOIN constructions ON selected_workers.construction_id = constructions.id
                           WHERE workers.user_id=? AND construction_id=?""", session["user_id"], session["constr_id"])

        return render_template("constr_info.html", construction_data=construction_data[0], posts=posts, photos=photos, username=username[0]["username"], selected_workers=selected_workers)


# Registering a worker into the database
@app.route("/register_worker", methods=["GET", "POST"])
@login_required
def register_worker():
    if request.method == "POST":

        # Get user input from .html
        data_input = {
            "name": request.form.get("name"),
            "role": request.form.get("role"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email")
        }

        # Ensure all inputs are fulfilled
        for data in data_input.values():
            if data == '':
                return render_template("error.html", code="401", error_message="Must fill all inputs")

        # Select all workers registered in user's account
        data_users = db.execute("SELECT name FROM workers WHERE user_id=?", session["user_id"])

        # In case of worker's name already exists in database
        for data in data_users:
            if data["name"].lower() == data_input["name"].lower():
                return render_template("error.html", code="401", error_message="Worker is already registered")

        # Insert worker's data into database
        db.execute("INSERT INTO workers (user_id, name, role, phone, email) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], data_input["name"].title(), data_input["role"], data_input["phone"], data_input["email"])

        # Return to the manage section
        flash(f"Worker {data_input['name'].title()} registered!")
        return redirect("/mng_workers")

    # In case of just opening the section
    else:
        return render_template("register_worker.html")


# Deleting (firing) a worker from the database
@app.route("/delete_worker", methods=["GET", "POST"])
@login_required
def delete_worker():

    # Catch worker's data assigned to user's account
    data_users = db.execute("SELECT * FROM workers WHERE user_id=?", session["user_id"])

    if request.method == "POST":
        # Querying worker's name
        worker = request.form.get("worker")

        # Deleting worker's data from database based on their name
        db.execute("DELETE FROM selected_workers WHERE worker_id IN (SELECT id FROM workers WHERE name=?)", worker)

        db.execute("DELETE FROM workers WHERE user_id=? AND name=?", session["user_id"], worker)

        # Return to manage section
        flash(f"Worker {worker} deleted")
        return redirect("/mng_workers")

    # In case of just opening the section where
    else:
        return render_template("delete_worker.html", workers=data_users)


# In case user wants to log out
@app.route("/logout")
@login_required
def logout():
    # Clearing the session
    session.clear()

    # Return to home section -> is not logged -> log in page
    flash("User logged out.")
    return redirect("/")
