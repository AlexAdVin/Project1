import os

from flask import Flask, session, render_template, request, logging, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

from passlib.hash import sha256_crypt


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#db.init_app(app)
db = SQLAlchemy(app)


@app.route('/')
def index():
    all_books = Books.query.all()
    return render_template('books.html', books=all_books)


#after login
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        print('post method')
        search_value = request.form['search_string']
        print(search_value)
        search = "%{}%".format(search_value)
        print(search)
        results = Books.query.filter(or_(Books.title.like(search),
                            Books.author.like(search))).all()
        #results = db.execute("SELECT * FROM books WHERE title LIKE search").fetchall()
        print(results)
        #if titledata is None:
        #    flash("The book does not exist", "danger")
        #    return render_template("search.html")
    return render_template('search.html', results=results)


if __name__ == '__main__':
    app.debug = True
    app.run()