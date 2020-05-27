import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

is_login = False


@app.route("/")
def index():
    return render_template("login.html", message=None)


@app.route("/login", methods=["POST", "GET"])
def login():
    # global is_login
    # if (is_login == True):
    #     return render_template("search_book.html", books=None)

    if 'username' in session:
        return render_template("search_book.html", message="Welcome" + str(session['username']) + " - " + str(session['user_id']))

    if request.method == 'POST':
        # Get data from page form :
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if it exists in database :
        try:
            user = db.execute("SELECT * FROM USERS WHERE username = :username AND password = :password",
                              {"username": username, "password": password}).fetchall()
        except:
            return render_template("error.html", message="cannot access database")
        if len(user) == 0:
            return render_template("login.html", message="Wrong User name or Password")
        else:
            # is_login = True
            session['user_id'] = user[0][0]
            session['username'] = username
            print("Login successful : " + str(session['user_id']))
            print("Login successful : " + str(session['username']))
            return render_template("search_book.html", message="Welcome" + str(session['username']) + " - " + str(session['user_id']))
    return render_template("login.html", message=None)


@app.route("/search_book", methods=["POST", "GET"])
def search_book():
    # global is_login
    # if (is_login == False):
    #     return render_template("login.html", message="Access forbidden, Please login first")

    if 'username' in session:
        books = None
        isbn = request.form.get("isbn")
        name = request.form.get("bookname")
        author = request.form.get("author")

        try:
            books = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND name ILIKE :name AND author ILIKE :author;",
                               {"isbn": "%"+str(isbn)+"%", "name": "%"+str(name)+"%", "author": "%"+str(author)+"%"}).fetchall()
        except:
            return render_template("error.html", message="cannot access database")
        return render_template("search_book.html", books=books)
    else:
        return render_template("login.html", message="Access forbidden, Please login first")


@app.route("/search_book/<int:book_id>")
def book_details(book_id):
    # global is_login
    # if (is_login == False):
    #     return render_template("login.html", message="Access forbidden, Please login first")

    if 'username' in session:

        book = db.execute("SELECT * FROM books WHERE id = :id",
                          {"id": book_id}).fetchone()
        if book is None:
            return render_template("error.html", message="No such book.")
        print("Book found : Book id=" + str(book_id) +
              " - Userid=" + str(session["user_id"]))
        return render_template("book_details.html", book=book, is_submitted=is_submitted(book_id, session["user_id"]))
    else:
        return render_template("login.html", message="Access forbidden, Please login first")


def is_submitted(book_id, user_id):
    review_count = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                              {"user_id": user_id, "book_id": book_id}).fetchone()
    if review_count is None:
        return False
    else:
        return True


@app.route("/register", methods=["POST", "GET"])
def register():
    # Get data from page form :
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        # Check if it exists in database :
        try:
            user = db.execute("SELECT * FROM USERS WHERE username = :username",
                              {"username": username}).fetchall()

        except:
            return render_template("error.html", message="cannot access database")
        if len(user) > 0:
            return render_template("register.html", message="User already exist, please try again")
        elif (len(username) < 1 or len(password) < 1):
            return render_template("register.html", message="User name and password are mandatory")
        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                       {"username": username, "password": password})
            db.commit()
            return render_template("login.html", message=None)

    return render_template("register.html", message=None)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    # global is_login
    # is_login = False

    # remove the username from the session if it is there
    session.pop('username', None)
    return render_template("login.html", message="Logout Success")


@app.route("/search_book/<int:book_id>", methods=["POST", "GET"])
def submit_review(book_id):
    # Get data from page form :
    if request.method == 'POST':
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        user_id = session["user_id"]

        # Check if it exists in database :
        try:
            reviews = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id ",
                                 {"user_id": user_id, "book_id": book_id}).fetchall()
            book = db.execute(
                "SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        except:
            return render_template("error.html", message="Cannot access database")
        if len(reviews) > 0: # Should never happen
            return render_template("error.html", message="You already submitted for this book")
        else:
            db.execute("INSERT INTO reviews (rating, opinion,user_id,book_id) VALUES (:rating, :comment, :user_id, :book_id)",
                       {"rating": rating, "comment": comment, "user_id": user_id, "book_id": book_id})
            db.commit()
            return render_template("book_details.html", book=book, is_submitted=True)

    return render_template("book_details.html", book=book)
