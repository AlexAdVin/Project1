import os

from flask import Flask, session, render_template, request, logging, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from passlib.hash import sha256_crypt

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")
    

@app.route("/register", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))

        if password == confirm:
            db.execute("INSERT INTO users(name,username,password) VALUES(:name,:username,:password)",
                            {"name":name,"username":username,"password":secure_password})
            db.commit()
            flash("you are registered and can login", "sucess")
            return redirect(url_for('login'))

        else:
            flash("password does not match", "danger")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
     
        usernamedata = db.execute("SELECT username FROM users WHERE username=:username", {"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username", {"username":username}).fetchone()

        if usernamedata is None:
            flash("The username does not exist", "danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                if sha256_crypt.verify(password,password_data):
                    session["log"] = True

                    flash("You are now logged in", "success")
                    return redirect(url_for('search'))
                else:
                    flash("Incorect username or password", "danger")
                    return render_template("login.html")

    return render_template("login.html")


#after login
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        s_book = request.form['search_string']

        titledata = db.execute("SELECT * FROM books WHERE s_book=title").fetchall()
        #if titledata is None:
        #    flash("The book does not exist", "danger")
        #    return render_template("search.html")

        return render_template("search.html", search_string=titledata)


@app.route("/search/<book_title>")
def bookfinder(book_title):
    # Search for a book by title of a book
    book_title = db.execute("SELECT * FROM books WHERE title = :title", {"title": book_title}).fetchone()

    return render_template("book.html", books=book_title)


#logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('index'))



@app.route("/books")
def booklist():
    """List all flights."""
    book_list = db.execute("SELECT * FROM books LIMIT 10").fetchall()
    return render_template("books.html", books=book_list)


@app.route("/books/<int:book_id>")
def book(book_id):
    """List details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    return render_template("book.html", book=book)



if __name__ == '__main__':
    app.debug = True
    app.run()

# postgres://khxxfluukbyqoh:1084ea7b53f5ce4fdbdef299f6c0fc5f334adc6d9d3400e3761b43bf93878c8e@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d62ujht21ufg6u
