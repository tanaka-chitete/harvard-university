import os
import requests
import urllib.parse
import decimal

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_quote(ticker):
    """Gets quote for TICKER."""

    # Contacts API
    try:
        response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(ticker)}/quote?token={os.getenv('API_KEY')}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parses response
    try:
        quote = response.json()
        stripped_quote = {
            "ticker": quote["symbol"],
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "change": quote["change"],
            "changePercent": quote["changePercent"],
            "ytdChangePercent": quote["ytdChange"],
            "isMarketOpen": quote["isUSMarketOpen"],
            "week52Low": quote["week52Low"],
            "week52High": quote["week52High"],
            "marketCap": quote["marketCap"],
            "latestTime": quote["latestTime"]
        }
        if quote["ytdChange"] != None:
            stripped_quote["ytdChange"] = quote["latestPrice"] - (quote["latestPrice"] / (1.0 + quote["ytdChange"]))
        else:
            stripped_quote["ytdChange"] = None

        return stripped_quote
    except (KeyError, TypeError, ValueError):
        return None

def get_info(ticker):
    """Gets information about TICKER."""

    # Contacts API
    try:
        response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(ticker)}/company?token={os.getenv('API_KEY')}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parses response
    try:
        info = response.json()
        stripped_info = {
            "exchange": info["exchange"],
            "industry": info["industry"],
            "sector": info["sector"],
            "CEO": info["CEO"],
            "website": info["website"],
            "state": info["state"],
        }

        # Replaces location with "N/A" if either city or state are None or ""
        if None in (info["city"], info["state"]) or "" in (info["city"], info["state"]):
            stripped_info["location"] = "N/A"
        else:
            stripped_info["location"] = info["city"] + ", " + info["state"]

        # Replaces None and "" pieces of information with "N/A"
        for key in stripped_info:
            if stripped_info[key] == None or stripped_info[key] == "":
                stripped_info[key] = "N/A"

        return stripped_info
    except (KeyError, TypeError, ValueError):
        return None

def format_real(real):
    if isinstance(real, str):
        formatted_real = f"{round(float(real.replace(',', '')), 2):,.2f}"
    else:
        formatted_real = f"{round(float(real), 2):,.2f}"
    return formatted_real

def format_whole(whole):
    return f"{whole:,}"

def format_percent(decimal):
    return f"{round(float(decimal) * 100.0, 2):,.2f}"

# Adapted from rtaft
# https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings-in-python/45846841
# Accessed 17/02/2021
def format_market_cap(market_cap):
    market_cap = float('{:.3g}'.format(market_cap))
    magnitude = 0
    while abs(market_cap) >= 1000:
        magnitude += 1
        market_cap /= 1000.0
    return '{}{}'.format('{:f}'.format(market_cap).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
# End of code adapted from above source

def to_market_status(boolean):
    if boolean:
        market_status = "OPEN"
    else:
        market_status = "CLOSED"
    return market_status

def add_positive_sign(value):
    # Ensures VALUE is a str as VALUE may be either an int or str
    value = str(value)
    if value[0] != "-":
        signed_value = "+" + value
    else:
        signed_value = value
    return signed_value