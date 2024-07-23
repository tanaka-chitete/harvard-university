import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def error(message, code=400):
    return render_template("apology.html", top=code, bottom=message)


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


def getRatios(symbol):
    """Look up ratios for symbol."""

    # Contact API
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{urllib.parse.quote_plus(symbol)}?apikey=3ba08c4fa13ed2576825ff347e79e507")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        ratiosFullList = response.json()

        # Ensure ratios of only the last 5 financial years are returned
        if len(ratiosFullList) > 5:
            del ratiosFullList[5:]

        ratiosPartial = dict()
        ratiosPartialList = []
        for i in range(len(ratiosFullList)):
            # Profitability ratios
            ratiosPartial["operatingProfitMargin"] = ratiosFullList[i]["operatingProfitMargin"]
            ratiosPartial["grossProfitMargin"] = ratiosFullList[i]["grossProfitMargin"]
            ratiosPartial["netProfitMargin"] = ratiosFullList[i]["netProfitMargin"]
            ratiosPartial["returnOnAssets"] = ratiosFullList[i]["returnOnAssets"]
            ratiosPartial["returnOnEquity"] = ratiosFullList[i]["returnOnEquity"]

            # Liquidity ratios
            ratiosPartial["currentRatio"] = ratiosFullList[i]["currentRatio"]
            ratiosPartial["quickRatio"] = ratiosFullList[i]["quickRatio"]

            # Leverage ratios
            ratiosPartial["debtRatio"] = ratiosFullList[i]["debtRatio"]
            ratiosPartial["debtEquityRatio"] = ratiosFullList[i]["debtEquityRatio"]
            ratiosPartial["interestCoverageRatio"] = ratiosFullList[i]["interestCoverage"]

            # Efficiency ratios
            ratiosPartial["inventoryTurnover"] = ratiosFullList[i]["inventoryTurnover"]
            ratiosPartial["receivablesTurnover"] = ratiosFullList[i]["receivablesTurnover"]
            ratiosPartial["payablesTurnover"] = ratiosFullList[i]["payablesTurnover"]
            ratiosPartial["assetTurnover"] = ratiosFullList[i]["assetTurnover"]

            # Market ratios (excluding Earnings per Share)
            ratiosPartial["priceEarningsRatio"] = ratiosFullList[i]["priceEarningsRatio"]
            ratiosPartial["dividendYield"] = ratiosFullList[i]["dividendYield"]

            # Add ratio of year to list of yearly ratios
            ratiosPartialList.append(ratiosPartial)
        return ratiosPartialList
    except (KeyError, TypeError, ValueError):
        return None








