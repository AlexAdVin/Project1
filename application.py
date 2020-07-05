import os

from flask import Flask, session, render_template, request, logging, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from passlib.hash import sha256_crypt

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# python3 -c 'import os; print(os.urandom(16))'
app.secret_key = b"\x04\x02\xd7 \xd4.\xb0\x9a\x08\xe4E\xe2\x91\x12i'"

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


#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
     
        usernamedata = db.execute("SELECT username FROM users WHERE username=:username", {"username":session['username']}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username", {"username":session['username']}).fetchone()

        if usernamedata is None:
            flash("The username does not exist", "danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                if sha256_crypt.verify(session['password'],password_data):
                    session["log"] = True

                    flash("You are now logged in", "success")
                    return redirect(url_for('search'))
                else:
                    flash("Incorect username or password", "danger")
                    return render_template("login.html")

    return render_template("login.html")


#logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('index'))


#after login
@app.route("/search", methods=["GET", "POST"])
def search():
    search_value = request.form.get("search_string")
    #print(search_value)
    if search_value == '':
        return render_template('search.html', message='Please enter required fields')

    query = "SELECT * FROM books WHERE title ILIKE '%{}%'".format(search_value)
    titledata = db.execute(query).fetchall()
    print(titledata)
    #if titledata is None:
        #flash("The book does not exist", "danger")
        #return render_template("search.html")
    return render_template("search.html", results=titledata)



@app.route("/search/<result_id>")
def details(result_id):
    # Search for a book by title of a book
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": result_id}).fetchone()

    return render_template("book.html", book=book)



@app.route("/submit/<book_id>", methods=["POST"])
def submit(book_id):
    rating = request.form.get("ratings")
    comment = request.form.get("comments")
    #book_id = request.form.get("book_id")
    print(book_id)

    if rating == '' or comment == '':
        return render_template('search.html', message='Please enter required fields')

    #try:
    #    book_id = int(request.form.get("review_id"))
    #except ValueError:
    #    return render_template("error.html", message="Invalid flight number.")

    # Add comment
    db.execute("INSERT INTO reviews (ratings, comments, review_id) VALUES (:rating, :comment, :review_id)", 
            {"rating": rating, "comment":comment, "review_id":book_id})
    print(f"Added comment: {comment} and {rating}")
    db.commit()

    return redirect(url_for('search'))






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


