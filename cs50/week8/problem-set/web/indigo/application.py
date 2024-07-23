import os

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, get_quote, get_info, format_real, format_whole, format_percent, format_market_cap, to_market_status, add_positive_sign
from datetime import datetime

# Loads environment variables from .env
load_dotenv()

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
app.jinja_env.filters["format_real"] = format_real
app.jinja_env.filters["format_whole"] = format_whole
app.jinja_env.filters["format_percent"] = format_percent
app.jinja_env.filters["format_market_cap"] = format_market_cap
app.jinja_env.filters["to_market_status"] = to_market_status
app.jinja_env.filters["add_positive_sign"] = add_positive_sign

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create engine object to manage connections to database and
# scoped session to separate user interactions with it
db_url = os.getenv("DB_URL")
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
            return apology("No username and/or password was entered.", 403)

        # Query database for user credentials
        credentials = cursor.execute("SELECT * FROM users WHERE username = :username",
                       {"username": request.form.get("username")}).fetchone()
        # credentials = results.fetchone()

        # Ensure username exists and password is correct
        if not credentials or not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Invalid username and/or password.", 403)

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
            return apology("No username, password and/or password confirmation was entered.", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Passwords do not match.", 403)

        # Query database for exising credentials with provided username (to verify whether it is already in use)
        existing_credentials = cursor.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()

        # Ensure username does not exist
        if existing_credentials:
            return apology("Username already in use.", 403)

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

    # Retreive user cash balance
    cash = float(cursor.execute("SELECT cash FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()[0])

    # Retreive user holdings
    holdings = cursor.execute("SELECT * FROM holdings WHERE username = :username ORDER BY ticker", {"username": session["username"]}).fetchall()

    # Retreive pricing information
    stocks = 0.00
    for i in range(len(holdings)):
        # Converts RowQuery to List to enable appending of elements
        holdings[i] = list(holdings[i])

        # Looks up holding
        quote = get_quote(holdings[i][2])

        # Retreive current price of holding
        holdings[i].append(quote["price"])

        # Calculate market value of total holding
        holdings[i].append(float(holdings[i][4]) * quote["price"])

        # Adds to cumulative holdings, replacing commas with empty strings
        stocks += holdings[i][6]

    total = stocks + cash

    if total > 0.0:
        stocks_allocation = stocks / total
        cash_allocation = cash / total
    # Prevents ZeroDivisionError when new account is created
    else:
        stocks_allocation = 0.0
        cash_allocation = 0.0

    # Calculates stock allocations
    for i in range(len(holdings)):
        # Calculates stock allocation taking into account only total stocks value
        holdings[i].append(holdings[i][6] / stocks)

        # Calculates stock allocation taking into account both total stocks value and cash balance
        holdings[i].append(holdings[i][6] / total)

    # Displays user holdings
    return render_template("index.html", total=total, stocks=stocks, stocks_allocation=stocks_allocation,
                           cash=cash, cash_allocation=cash_allocation, holdings=holdings)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Attempts to get quote
        quote = get_quote(request.form.get("ticker"))

        # Ensures valid ticker was submitted
        if not quote:
            return apology("Ticker provided is invalid.", 403)

        # Redirect user to requested quote
        else:
            # Gets info
            info = get_info(request.form.get("ticker"))

            return render_template("quoted.html", quote=quote, info=info)

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
            return apology("No ticker, shares, password and/or password confirmation was provided.", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid.", 403)

        # Attempt to retreive quote
        quote = get_quote(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not quote:
            return apology("Ticker provided was invalid.", 403)

        # Ensure user has enough funds for purchase
        elif credentials[3] < (float(request.form.get("shares")) * quote["price"]):
            return apology("Insufficient funds available for purchase.", 403)

        else:
            # Remove funds from user account
            cursor.execute("UPDATE users SET cash = cash - :cash_dec WHERE id = :user_id",
                           {"cash_dec": float(request.form.get("shares")) * quote["price"],
                            "user_id": session["user_id"]})
            cursor.commit()

            # Query database for user holdings of stock
            existing_holding = cursor.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                           {"username": session["username"], "ticker": quote["ticker"]}).fetchone()

            # Add new holding
            if not (existing_holding):
                cursor.execute("INSERT INTO holdings (username, ticker, company_name, shares) VALUES \
                                                     (:username, :ticker, :company_name, :shares)",
                               {"username": session["username"], "ticker": quote["ticker"],
                                "company_name": quote["name"], "shares": int(request.form.get("shares"))})
                cursor.commit()

            # Increase existing holding
            else:
                cursor.execute("UPDATE holdings SET shares = shares + :shares_inc WHERE \
                               username = :username AND ticker = :ticker",
                               {"shares_inc": int(request.form.get("shares")),
                                "username": session["username"],
                                "ticker": quote["ticker"]})
                cursor.commit()

            # Add to history
            cursor.execute("INSERT INTO history (username, ticker, company_name, holding_change, cash_change, time, date) \
                           VALUES (:username, :ticker, :company_name, :holding_change, :cash_change, :time, :date)",
                           {"username": session["username"], "ticker": quote["ticker"],
                            "company_name": quote["name"], "holding_change": request.form.get("shares"),
                            "cash_change": -1.0 * (float(request.form.get("shares")) * quote["price"]),
                            "time": datetime.utcnow().strftime("%H:%M:%S"),
                            "date": datetime.utcnow().strftime("%d/%m/%Y")})
            cursor.commit()

            # Retreive transaction details
            new_holding = cursor.execute("SELECT * FROM history WHERE username = :username AND \
                           ticker = :ticker ORDER BY id DESC LIMIT 1",
                           {"username": session["username"], "ticker": quote["ticker"]}).fetchone()

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
            return apology("No ticker, shares, password and/or password confirmation was provided.", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid.", 403)

        # Attempt to retreive quote
        quote = get_quote(request.form.get("ticker"))

        # Ensure valid ticker was submitted
        if not quote:
            return apology("Provided ticker is invalid.", 403)

        # Query database for user holdings of stock
        existing_holding = cursor.execute("SELECT * FROM holdings WHERE username = :username AND ticker = :ticker",
                        {"username": session["username"], "ticker": quote["ticker"]}).fetchone()

        # Ensure user owns holding
        if not existing_holding:
            return apology("Provided ticker does not belong to any currently owned holding.", 403)

        # Ensure user only sells amount of shares owned
        elif int(request.form.get("shares")) > existing_holding[4]:
            return apology("Provided shares exceeds what is owned of holding.", 403)

        else:
            # Sell all of holding
            if int(request.form.get("shares")) == existing_holding[4]:
                cursor.execute("DELETE FROM holdings WHERE username = :username AND ticker = :ticker",
                                {"username": session["username"], "ticker": quote["ticker"]})
                cursor.commit()

            # Sell portion of holding
            else:
                cursor.execute("UPDATE holdings SET shares = shares - :shares_dec WHERE \
                               username = :username AND ticker = :ticker",
                               {"shares_dec": int(request.form.get("shares")),
                                "username": session["username"],
                                "ticker": quote["ticker"]})
                cursor.commit()

            # Adds funds to user account
            cursor.execute("UPDATE users SET cash = cash + :cash_inc WHERE id = :user_id",
                           {"cash_inc": float(request.form.get("shares")) * quote["price"],
                            "user_id": session["user_id"]})
            cursor.commit()

            # Add to history
            cursor.execute("INSERT INTO history (username, ticker, company_name, holding_change, cash_change, time, date) \
                           VALUES (:username, :ticker, :company_name, :holding_change, :cash_change, :time, :date)",
                           {"username": session["username"], "ticker": quote["ticker"],
                            "company_name": quote["name"], "holding_change": -1 * int(request.form.get("shares")),
                            "cash_change": float(request.form.get("shares")) * quote["price"],
                            "time": datetime.utcnow().strftime("%H:%M:%S"),
                            "date": datetime.utcnow().strftime("%d/%m/%Y")})
            cursor.commit()

            # Retreive transaction details
            old_holding = cursor.execute("SELECT * FROM history WHERE username = :username AND \
                           ticker = :ticker ORDER BY id DESC LIMIT 1",
                           {"username": session["username"], "ticker": quote["ticker"]}).fetchone()

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
    history = cursor.execute("SELECT * FROM history WHERE username = :username ORDER BY time DESC", {"username": session["username"]}).fetchall()

    # Display user history
    return render_template("history.html", history=history)


@app.route("/fund", methods=["GET", "POST"])
@login_required
def fund():
    """Add funds."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username, password and confirmation were submitted
        if not request.form.get("amount") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("No amount, password and/or password confirmation was provided.", 403)

        # Ensure password confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Provided password and password confirmation do not match.", 403)

        # Query database for user account details
        credentials = cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()

        # Ensure password is same as one of user account
        if not check_password_hash(credentials[2], request.form.get("password")):
            return apology("Provided password and password confirmation are invalid.", 403)

        # Adds funds to user account
        cursor.execute("UPDATE users SET cash = cash + :cash_inc WHERE id = :user_id",
                       {"cash_inc": request.form.get("amount"), "user_id": session["user_id"]})
        cursor.commit()

        # Redirect user fund addition confirmation
        return render_template("funded.html", cash_increase=float(request.form.get("amount")))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("fund.html")

def errorhandler(e):
    """Handle errors"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
