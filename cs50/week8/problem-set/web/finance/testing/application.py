import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Additional imports
from datetime import datetime
from helpers import usd_no_sign

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return apology("No username and/or password was provided", 403)

        # Query database for user credentials
        credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                 username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(credentials) != 1 or not check_password_hash(credentials[0]["hash"], request.form.get("password")):
            return apology("Username and/or password is invalid", 403)

        # Remember which user has logged in
        session["user_id"] = credentials[0]["id"]
        session["username"] = credentials[0]["username"]

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

        # Ensure username password and confirmation were submitted
        if not request.form.get("username") or \
           not request.form.get("password") or \
           not request.form.get("confirmation"):
            return apology("No username, password and/or password confirmation was provided", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided passwords do not match", 403)

        # Query database for credentials with provided username (to verify whether it is already in use)
        credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                 username=request.form.get("username"))

        # Ensure username does not exist
        if len(credentials) != 0:
            return apology("Provided username is already in use", 403)

        # Add login details to database
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :passwordHash)",
                       username=request.form.get("username"),
                       passwordHash=generate_password_hash(password=request.form.get("password")))

        # Query database for credentials (to remember session)
        credentials = db.execute("SELECT * FROM users WHERE username = :username",
                                 username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = credentials[0]["id"]
        session["username"] = credentials[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Retreive user balance
    funds = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])

    # Retreive user holdings
    holdings = db.execute("SELECT * FROM holdings WHERE username = :username ORDER BY ticker",
                          username=session["username"])

    # Retreive pricing information
    stocks = 0.00
    total = funds[0]["cash"]
    for holding in range(len(holdings)):
        # Looks up holding
        results = lookup(holdings[holding]["ticker"])

        # Retreive current price of holding
        holdings[holding]["current_price"] = usd_no_sign(results["price"])

        # Calculate market value of total holding
        holdings[holding]["market_value"] = usd_no_sign(float(holdings[holding]["shares"]) * results["price"])

        # Adds to cumulative holdings
        stocks += float(holdings[holding]["market_value"].replace(",",""))

    # Adds to cumulative balance add holdings
    total = funds[0]["cash"] + stocks

    # Displays user holdings
    return render_template("index.html", funds=usd(funds[0]["cash"]), holdings=holdings, stocks=usd(stocks),
                           total=usd(total))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Attempt to retreive quote
        stock_quote = lookup(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not stock_quote:
            return apology("Ticker provided was invalid.", 403)

        # Redirect user to requested quote
        else:
            return render_template("quoted.html", name=stock_quote["name"], ticker=stock_quote["ticker"],
                                   price=usd(stock_quote["price"]))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure ticker, shares, password and confirmation were submitted
        if not request.form.get("ticker") or not request.form.get("shares") or not request.form.get("password") or \
           not request.form.get("confirmation"):
            return apology("No ticker, shares, password and/or password confirmation was provided", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = db.execute("SELECT * FROM users WHERE id = :user_id",
                                 user_id=session["user_id"])

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[0]["hash"], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Attempt to retreive quote
        stock_quote = lookup(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not stock_quote:
            return apology("Ticker provided was invalid.", 403)

        # Ensure user has enough funds for purchase
        elif credentials[0]["cash"] < (float(request.form.get("shares")) * stock_quote["price"]):
            return apology("Insufficient funds available for purchase.", 403)

        else:
            # Remove funds from user account
            db.execute("UPDATE users SET cash = cash - :cash_dec WHERE id = :user_id",
                       cash_dec=float(request.form.get("shares")) * stock_quote["price"],
                       user_id=session["user_id"])

            # Query database for user holdings of stock
            existing_holding = db.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                                          username=session["username"], ticker=stock_quote["ticker"])

            # Add new holding
            if not (existing_holding):
                db.execute("INSERT INTO holdings (username, ticker, name, shares) VALUES \
                                                 (:username, :ticker, :name, :shares)",
                            username=session["username"], ticker=stock_quote["ticker"],
                            name=stock_quote["name"], shares=int(request.form.get("shares")))

            # Increase existing holding
            else:
                db.execute("UPDATE holdings SET shares = shares + :shares_inc WHERE \
                           username = :username AND ticker = :ticker",
                           shares_inc=int(request.form.get("shares")),
                           username=session["username"],
                           ticker=stock_quote["ticker"])

            # Add to history
            db.execute("INSERT INTO history (username, ticker, name, shares, price, date, time) \
                       VALUES (:username, :ticker, :name, :shares, :price, :date, :time)",
                       username=session["username"], ticker=stock_quote["ticker"],
                       name=stock_quote["name"], shares=request.form.get("shares"),
                       price=usd_no_sign(float(request.form.get("shares")) * stock_quote["price"]),
                       date=datetime.utcnow().strftime("%d/%m/%Y"), time=datetime.utcnow().strftime("%H:%M:%S"))

            # Retreive transaction details
            new_holding = db.execute("SELECT * FROM history WHERE username = :username AND ticker = :ticker \
                                     ORDER BY id DESC LIMIT 1", username=session["username"], ticker=stock_quote["ticker"])

        # Redirect user to confirmation
        return render_template("bought.html", holding=new_holding)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure ticker, shares, password and confirmation were submitted
        if not request.form.get("ticker") or not request.form.get("shares") or not request.form.get("password") or \
           not request.form.get("confirmation"):
            return apology("No ticker, shares, password and/or password confirmation was provided", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = db.execute("SELECT * FROM users WHERE id = :user_id",
                                 user_id=session["user_id"])

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[0]["hash"], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Attempt to retreive quote
        stock_quote = lookup(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not stock_quote:
            return apology("Provided ticker is invalid", 403)

        # Query database for user holding
        existing_holding = db.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                                      username=session["username"], ticker=stock_quote["ticker"])

        # Ensure user owns holding
        if not existing_holding:
            return apology("Provided ticker does not belong to any currently owned holding", 403)

        # Ensure user only sells amount of shares owned
        elif int(request.form.get("shares")) > existing_holding[0]["shares"]:
            return apology("Provided shares exceeds what is owned of holding", 403)

        else:
            # Sell all of holding
            if int(request.form.get("shares")) == existing_holding[0]["shares"]:
                db.execute("DELETE FROM holdings WHERE username = :username AND ticker = :ticker",
                           username=session["username"], ticker=stock_quote["ticker"])

            # Sell portion of holding
            else:
                db.execute("UPDATE holdings SET shares = shares - :shares_dec WHERE \
                           username = :username AND ticker = :ticker",
                           shares_dec=int(request.form.get("shares")),
                           username=session["username"],
                           ticker=stock_quote["ticker"])

            # Adds funds to user account
            db.execute("UPDATE users SET cash = cash + :cash_inc WHERE id = :user_id",
                       cash_inc=float(request.form.get("shares")) * stock_quote["price"],
                       user_id=session["user_id"])

            # Add to history
            db.execute("INSERT INTO history (username, ticker, name, shares, price, date, time) \
                       VALUES (:username, :ticker, :name, :shares, :price, :date, :time)",
                       username=session["username"], ticker=stock_quote["ticker"],
                       name=stock_quote["name"], shares="-"+request.form.get("shares"),
                       price=usd_no_sign(float(request.form.get("shares")) * stock_quote["price"]),
                       date=datetime.utcnow().strftime("%d/%m/%Y"), time=datetime.utcnow().strftime("%H:%M:%S"))

            # Retreive transaction details
            new_holding = db.execute("SELECT * FROM history WHERE username = :username AND ticker = :ticker \
                                     ORDER BY id DESC LIMIT 1", username=session["username"], ticker=stock_quote["ticker"])

        # Redirect user to confirmation
        return render_template("sold.html", holding=new_holding)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Retreive user history
    history = db.execute("SELECT * FROM history WHERE username = :username",
                          username=session["username"])

    # Display user history
    return render_template("history.html", history=history)


@app.route("/add-funds", methods=["GET", "POST"])
@login_required
def add_funds():
    """Add funds."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username, password and confirmation were submitted
        if not request.form.get("amount") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("No amount, password and/or password confirmation was provided", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = db.execute("SELECT * FROM users WHERE id = :user_id",
                                 user_id=session["user_id"])

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[0]["hash"], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Adds funds to user account
        db.execute("UPDATE users SET cash = cash + :amount WHERE id = :user_id",
                   amount=request.form.get("amount"),
                   user_id=session["user_id"])

        # Redirect user fund addition confirmation
        return render_template("funds-added.html", amount=usd(float(request.form.get("amount"))))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add-funds.html")


@app.route("/information", methods=["GET", "POST"])
@login_required
def currency():
    """Show usage information."""
    return render_template("information.html")

def errorhandler(e):
    """Handle errors"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
