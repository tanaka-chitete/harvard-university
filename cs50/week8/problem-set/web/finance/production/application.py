import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
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

# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["usd_no_sign"] = usd_no_sign

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create engine object to manage connections to database and
# scoped session to separate user interactions with it
db_url = "postgres://raswmviujirjxc:9e5951f3a1cacccb76f950e493fdcae164428f2ccadb64713b7bcc4ee4bff2e8@ec2-18-209-187-54.compute-1.amazonaws.com:5432/d9ukgt50us6rs4"
engine = create_engine(db_url)
cursor = scoped_session(sessionmaker(bind=engine))
connection = engine.connect()


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
        credentials = cursor.execute("SELECT * FROM users WHERE username = :username",
                       {"username": request.form.get("username")}).fetchone()
        # credentials = results.fetchone()

        # Ensure username exists and password is correct
        if not credentials or not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Username and/or password is invalid", 403)

        # Remember which user has logged in
        session["user_id"] = credentials[0]
        session["username"] = credentials[1]

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

        # Query database for exising credentials with provided username (to verify whether it is already in use)
        existing_credentials = cursor.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()

        # Ensure username does not exist
        if existing_credentials:
            return apology("Provided username is already in use", 403)

        # Add login details to database
        else:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)",
                            {"username": request.form.get("username"),
                            "password_hash": generate_password_hash(password=request.form.get("password"))})
            cursor.commit()

        # Query database for new credentials (to remember session)
        new_credentials = cursor.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()

        # Remember which user has logged in
        session["user_id"] = new_credentials[0]
        session["username"] = new_credentials[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Retreive user credentials
    credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

    # Retreive user holdings
    holdings = cursor.execute("SELECT * FROM holdings WHERE username = :username ORDER BY ticker", {"username": session["username"]}).fetchall()

    # Retreive pricing information
    stocks = 0.00
    current_prices = []
    market_values = []
    for holding in range(len(holdings)):
        # Looks up holding
        stock_quote = lookup(holdings[holding][2])

        # Retreive current price of holding
        current_price = usd_no_sign(stock_quote["price"])
        current_prices.append(current_price)

        # Calculate market value of total holding
        market_value = usd_no_sign(float(holdings[holding][4]) * stock_quote["price"])
        market_values.append(market_value)

        # Adds to cumulative holdings, replacing commas with empty strings
        stocks += float(market_values[holding].replace(",",""))

    # Adds to cumulative balance add holdings
    total = float(credentials[3]) + stocks

    # Displays user holdings
    return render_template("index.html", funds=usd(credentials[3]), holdings=holdings, current_prices=current_prices,
                           market_values=market_values, stocks=usd(stocks), total=usd(total))


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
            return apology("Ticker provided is invalid.", 403)

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
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Attempt to retreive quote
        stock_quote = lookup(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not stock_quote:
            return apology("Ticker provided was invalid.", 403)

        # Ensure user has enough funds for purchase
        elif credentials[3] < (float(request.form.get("shares")) * stock_quote["price"]):
            return apology("Insufficient funds available for purchase.", 403)

        else:
            # Remove funds from user account
            cursor.execute("UPDATE users SET cash = cash - :cash_dec WHERE id = :user_id",
                           {"cash_dec": float(request.form.get("shares")) * stock_quote["price"],
                            "user_id": session["user_id"]})
            cursor.commit()

            # Query database for user holdings of stock
            existing_holding = cursor.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                           {"username": session["username"], "ticker": stock_quote["ticker"]}).fetchone()

            # Add new holding
            if not (existing_holding):
                cursor.execute("INSERT INTO holdings (username, ticker, company_name, shares) VALUES \
                                                     (:username, :ticker, :company_name, :shares)",
                               {"username": session["username"], "ticker": stock_quote["ticker"],
                                "company_name": stock_quote["name"], "shares": int(request.form.get("shares"))})
                cursor.commit()

            # Increase existing holding
            else:
                cursor.execute("UPDATE holdings SET shares = shares + :shares_inc WHERE \
                               username = :username AND ticker = :ticker",
                               {"shares_inc": int(request.form.get("shares")),
                                "username": session["username"],
                                "ticker": stock_quote["ticker"]})
                cursor.commit()

            # Add to history
            cursor.execute("INSERT INTO history (username, ticker, company_name, shares, price, date, time) \
                           VALUES (:username, :ticker, :company_name, :shares, :price, :date, :time)",
                           {"username": session["username"], "ticker": stock_quote["ticker"],
                            "company_name": stock_quote["name"], "shares": request.form.get("shares"),
                            "price": float(request.form.get("shares")) * stock_quote["price"],
                            "date": datetime.utcnow().strftime("%d/%m/%Y"),
                            "time": datetime.utcnow().strftime("%H:%M:%S")})
            cursor.commit()

            # Retreive transaction details
            new_holding = cursor.execute("SELECT * FROM history WHERE username = :username AND \
                           ticker = :ticker ORDER BY id DESC LIMIT 1",
                           {"username": session["username"], "ticker": stock_quote["ticker"]}).fetchone()

        # Redirect user to confirmation
        return render_template("bought.html", new_holding=new_holding)

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
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Attempt to retreive quote
        stock_quote = lookup(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not stock_quote:
            return apology("Provided ticker is invalid", 403)

        # Query database for user holdings of stock
        existing_holding = cursor.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                        {"username": session["username"], "ticker": stock_quote["ticker"]}).fetchone()

        # Ensure user owns holding
        if not existing_holding:
            return apology("Provided ticker does not belong to any currently owned holding", 403)

        # Ensure user only sells amount of shares owned
        elif int(request.form.get("shares")) > existing_holding[4]:
            return apology("Provided shares exceeds what is owned of holding", 403)

        else:
            # Sell all of holding
            if int(request.form.get("shares")) == existing_holding[4]:
                cursor.execute("DELETE FROM holdings WHERE username = :username AND ticker = :ticker",
                                {"username": session["username"], "ticker": stock_quote["ticker"]})
                cursor.commit()

            # Sell portion of holding
            else:
                cursor.execute("UPDATE holdings SET shares = shares - :shares_dec WHERE \
                               username = :username AND ticker = :ticker",
                               {"shares_dec": int(request.form.get("shares")),
                                "username": session["username"],
                                "ticker": stock_quote["ticker"]})
                cursor.commit()

            # Adds funds to user account
            cursor.execute("UPDATE users SET cash = cash + :cash_inc WHERE id = :user_id",
                           {"cash_inc": float(request.form.get("shares")) * stock_quote["price"],
                            "user_id": session["user_id"]})
            cursor.commit()

            # Add to history
            cursor.execute("INSERT INTO history (username, ticker, company_name, shares, price, date, time) \
                           VALUES (:username, :ticker, :company_name, :shares, :price, :date, :time)",
                           {"username": session["username"], "ticker": stock_quote["ticker"],
                            "company_name": stock_quote["name"], "shares": request.form.get("shares"),
                            "price": float(request.form.get("shares")) * stock_quote["price"],
                            "date": datetime.utcnow().strftime("%d/%m/%Y"),
                            "time": datetime.utcnow().strftime("%H:%M:%S")})
            cursor.commit()

            # Retreive transaction details
            old_holding = cursor.execute("SELECT * FROM history WHERE username = :username AND \
                           ticker = :ticker ORDER BY id DESC LIMIT 1",
                           {"username": session["username"], "ticker": stock_quote["ticker"]}).fetchone()

        # Redirect user to confirmation
        return render_template("sold.html", old_holding=old_holding)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Retreive user history
    history = cursor.execute("SELECT * FROM history WHERE username = :username", {"username": session["username"]}).fetchall()

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
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid", 403)

        # Adds funds to user account
        cursor.execute("UPDATE users SET cash = cash + :cash_inc WHERE id = :user_id",
                       {"cash_inc": request.form.get("amount"), "user_id": session["user_id"]})
        cursor.commit()

        # Redirect user fund addition confirmation
        return render_template("funds-added.html", cash_inc=usd(float(request.form.get("amount"))))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add-funds.html")


@app.route("/information", methods=["GET", "POST"])
@login_required
def information():
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
