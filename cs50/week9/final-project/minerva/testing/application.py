import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import error, loginRequired, getListOfRatios, pad

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# # Create engine object to manage connections to database and
# # scoped session to separate user interactions with it
# db_url = "postgres://jptnvlrnaipapy:5c9a0cfe530177cbf83e774c1ae6b28cb14644beb55c83de9b5c3bdc65f1544d@ec2-34-197-141-7.compute-1.amazonaws.com:5432/de6iqf8h321q42"
# engine = create_engine(db_url)
# cursor = scoped_session(sessionmaker(bind=engine))
# connection = engine.connect()

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalproject.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return error("No username and/or password was provided", 403)

        # Query database for user credentials
        credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                  username=request.form.get("username"))

        # Ensure username exists and password is correct
        if not credentials or not check_password_hash(credentials[0]["password_hash"], request.form.get("password")):
            return error("Username and/or password is invalid", 403)

        # Remember which user has logged in
        session["user_id"] = credentials[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username, password and confirmation were submitted
        if not request.form.get("username") or \
           not request.form.get("password") or \
           not request.form.get("confirmation"):
            return error("No username, password and/or password confirmation was provided", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return error("Provided passwords do not match", 403)

        # Query database for existing credentials with provided username (to verify if it's already in use)
        existing_credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                           username=request.form.get("username"))

        # Ensure username does not exist
        if existing_credentials:
            return error("Provided username is already in use", 403)

        # Add login details to database
        else:
            db.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)",
                        username=request.form.get("username"),
                        password_hash=generate_password_hash(password=request.form.get("password")))

        # Query database for (new) user's credentials (to remember session)
        new_credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                      username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = new_credentials[0]["id"]

        # Redirect user to login form
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/")
@loginRequired
def index():
    """Show ratio information"""
    return render_template("index.html")


@app.route("/analyse", methods=["GET", "POST"])
@loginRequired
def analyse_financial_years():
    """Get financial ratios"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure ticker was submitted
        if not request.form.get("ticker"):
            return error("No ticker was provided.", 403)

        # Attempt to retreive quote
        listOfRatios = getListOfRatios(request.form.get("ticker").upper())

        # Ensure valid ticker was submitted (matches existing ticker of a publicly traded company)
        if not listOfRatios:
            return error("Ticker provided is invalid.", 403)

        # Ensure correct template is rendered based on the number of years for which ratios were returned
        numOfYears = len(listOfRatios)
        template = "analysisof" + str(numOfYears) + "years.html"

        # Redirect user to analysis
        return render_template(template, listOfRatios=listOfRatios)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("analyse.html")


@app.route("/compare", methods=["GET", "POST"])
@loginRequired
def compare_quarters():
    """Compare financial ratios"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        numOfCompanies = 2
        # Ensure tickers for at least two companies were submitted
        if not request.form.get("tickerOne") or not request.form.get("tickerTwo"):
            return error("Tickers one and/or two were not submitted.", 403)

        # Attempt to retreive quote for first company
        listOfRatiosForCompanyOne = getListOfRatios(request.form.get("tickerOne").upper())
        if not listOfRatiosForCompanyOne:
            return error("Ticker one is invalid.", 403)

        # Attempt to retreive quote for second company
        listOfRatiosForCompanyTwo = getListOfRatios(request.form.get("tickerTwo").upper())
        if not listOfRatiosForCompanyTwo:
            return error("Ticker two is invalid.", 403)

        # Attempt to retreive quote for (optional) third company
        listOfRatiosForCompanyThree = []
        if request.form.get("tickerThree"):
            listOfRatiosForCompanyThree = getListOfRatios(request.form.get("tickerThree").upper())
            if not listOfRatiosForCompanyThree:
                return error("Ticker three is invalid.", 403)
            numOfCompanies += 1

        # Attempt to retreive quote for (optional) fourth company
        listOfRatiosForCompanyFour = []
        if request.form.get("tickerFour"):
            # Ensure tickers are provided in order
            if not request.form.get("tickerThree"):
                return error("Tickers must be provided in order")
            listOfRatiosForCompanyFour = getListOfRatios(request.form.get("tickerFour").upper())
            if not listOfRatiosForCompanyFour:
                return error("Ticker four is invalid.", 403)
            numOfCompanies += 1

        # Attempt to retreive quote for (optional) fifth company
        listOfRatiosForCompanyFive = []
        if request.form.get("tickerFive"):
            # Ensure tickers are provided in order
            if not request.form.get("tickerFour") or not request.form.get("tickerThree"):
                return error("Tickers must be provided in order")
            listOfRatiosForCompanyFive = getListOfRatios(request.form.get("tickerFive").upper())
            if not listOfRatiosForCompanyFive:
                return error("Ticker five is invalid.", 403)
            numOfCompanies += 1

        # Redirect user to comparison (5 companies)
        if numOfCompanies == 5:
            # Ensure correct template is rendered based on the number of years and companies returned
            numOfYears = min(len(listOfRatiosForCompanyOne), len(listOfRatiosForCompanyTwo), \
                             len(listOfRatiosForCompanyThree), len(listOfRatiosForCompanyFour), \
                             len(listOfRatiosForCompanyFive))
            template = "comparisonof5companiesover" + str(numOfYears) + "years.html"

            return render_template(template, listOfRatiosForCompanyOne=listOfRatiosForCompanyOne, \
                                   listOfRatiosForCompanyTwo=listOfRatiosForCompanyTwo, \
                                   listOfRatiosForCompanyThree=listOfRatiosForCompanyThree, \
                                   listOfRatiosForCompanyFour=listOfRatiosForCompanyFour, \
                                   listOfRatiosForCompanyFive=listOfRatiosForCompanyFive)

        # Redirect user to comparison (4 companies)
        elif numOfCompanies == 4:
            # Ensure correct template is rendered based on the number of years and companies returned
            numOfYears = min(len(listOfRatiosForCompanyOne), len(listOfRatiosForCompanyTwo), \
                             len(listOfRatiosForCompanyThree), len(listOfRatiosForCompanyFour))
            template = "comparisonof4companiesover" + str(numOfYears) + "years.html"

            return render_template(template, listOfRatiosForCompanyOne=listOfRatiosForCompanyOne, \
                                   listOfRatiosForCompanyTwo=listOfRatiosForCompanyTwo, \
                                   listOfRatiosForCompanyThree=listOfRatiosForCompanyThree, \
                                   listOfRatiosForCompanyFour=listOfRatiosForCompanyFour)

        # Redirect user to comparison (3 companies)
        elif numOfCompanies == 3:
            # Ensure correct template is rendered based on the number of years and companies returned
            numOfYears = min(len(listOfRatiosForCompanyOne), len(listOfRatiosForCompanyTwo), \
                             len(listOfRatiosForCompanyThree))
            template = "comparisonof3companiesover" + str(numOfYears) + "years.html"

            return render_template(template, listOfRatiosForCompanyOne=listOfRatiosForCompanyOne, \
                                   listOfRatiosForCompanyTwo=listOfRatiosForCompanyTwo, \
                                   listOfRatiosForCompanyThree=listOfRatiosForCompanyThree)

        # Redirect user to comparison (2 companies)
        else:
            # Ensure correct template is rendered based on the number of years and companies returned
            numOfYears = min(len(listOfRatiosForCompanyOne), len(listOfRatiosForCompanyTwo))
            template = "comparisonof2companiesover" + str(numOfYears) + "years.html"

            return render_template(template, listOfRatiosForCompanyOne=listOfRatiosForCompanyOne, \
                                   listOfRatiosForCompanyTwo=listOfRatiosForCompanyTwo)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("compare.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
