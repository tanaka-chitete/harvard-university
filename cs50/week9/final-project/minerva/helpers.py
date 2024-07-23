import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def error(message, code=400):
    return render_template("error.html", top=code, bottom=message)


def loginRequired(f):
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


def getListOfRatios(symbol):
    """Look up ratios for symbol."""

    # Contact API
    try:
        responseForRatios = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{urllib.parse.quote_plus(symbol)}?apikey={os.getenv('API_KEY')}")
        responseForRatios.raise_for_status()

        responseForIncomeStatements = requests.get(f"https://financialmodelingprep.com/api/v3/income-statement/{urllib.parse.quote_plus(symbol)}?apikey={os.getenv('API_KEY')}")
        responseForIncomeStatements.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        listOfAllRatiosForAllYears = responseForRatios.json()
        listOfIncomeStatementsForAllYears = responseForIncomeStatements.json()

        # Ensure ratios of only the last 10 financial years will be returned
        if len(listOfAllRatiosForAllYears) > 10:
            del listOfAllRatiosForAllYears[10:]

        # Ensure earnings per share of only the last 10 financial years will be returned
        if len(listOfIncomeStatementsForAllYears) > 10:
            del listOfIncomeStatementsForAllYears[10:]

        # List of dictionaries to necessary ratios for necessary years (at most the last 10)
        listOfSomeRatiosForTenYears = []

        # Get only the necessary ratios
        for i in range(len(listOfAllRatiosForAllYears)):
            # Dictionary to store necessary ratios for one year (inside for loop so values persist as unique)
            someRatiosForOneYear = dict()

            someRatiosForOneYear["ticker"] = listOfAllRatiosForAllYears[i]["symbol"]
            someRatiosForOneYear["date"] = listOfAllRatiosForAllYears[i]["date"][0:4]

            # Profitability ratios
            someRatiosForOneYear["operatingProfitMargin"] = \
            parseRatio(listOfAllRatiosForAllYears[i]["operatingProfitMargin"])
            someRatiosForOneYear["grossProfitMargin"] = parseRatio(listOfAllRatiosForAllYears[i]["grossProfitMargin"])
            someRatiosForOneYear["netProfitMargin"] = parseRatio(listOfAllRatiosForAllYears[i]["netProfitMargin"])
            someRatiosForOneYear["returnOnAssets"] = parseRatio(listOfAllRatiosForAllYears[i]["returnOnAssets"])
            someRatiosForOneYear["returnOnEquity"] = parseRatio(listOfAllRatiosForAllYears[i]["returnOnEquity"])

            # Liquidity ratios
            someRatiosForOneYear["currentRatio"] = parseRatio(listOfAllRatiosForAllYears[i]["currentRatio"])
            someRatiosForOneYear["quickRatio"] = parseRatio(listOfAllRatiosForAllYears[i]["quickRatio"])

            # Leverage ratios
            someRatiosForOneYear["debtAssetRatio"] = parseRatio(listOfAllRatiosForAllYears[i]["debtRatio"])
            someRatiosForOneYear["debtEquityRatio"] = parseRatio(listOfAllRatiosForAllYears[i]["debtEquityRatio"])
            someRatiosForOneYear["interestCoverageRatio"] = \
            parseRatio(listOfAllRatiosForAllYears[i]["interestCoverage"])

            # Efficiency ratios
            someRatiosForOneYear["inventoryTurnover"] = parseRatio(listOfAllRatiosForAllYears[i]["inventoryTurnover"])
            someRatiosForOneYear["receivablesTurnover"] = \
            parseRatio(listOfAllRatiosForAllYears[i]["receivablesTurnover"])
            someRatiosForOneYear["payablesTurnover"] = parseRatio(listOfAllRatiosForAllYears[i]["payablesTurnover"])
            someRatiosForOneYear["assetTurnover"] = parseRatio(listOfAllRatiosForAllYears[i]["assetTurnover"])

            # Market ratios
            if i < len(listOfIncomeStatementsForAllYears):
                someRatiosForOneYear["earningsPerShare"] = parseRatio(listOfIncomeStatementsForAllYears[i]["eps"])
            else:
                someRatiosForOneYear["earningsPerShare"] = "N/A"
            someRatiosForOneYear["priceEarningsRatio"] = \
            parseRatio(listOfAllRatiosForAllYears[i]["priceEarningsRatio"])
            someRatiosForOneYear["dividendYield"] = parseRatio(listOfAllRatiosForAllYears[i]["dividendYield"])

            # Add ratio of year to list of yearly ratios
            listOfSomeRatiosForTenYears.append(someRatiosForOneYear)

        return listOfSomeRatiosForTenYears
    except (KeyError, TypeError, ValueError):
        return None


def parseRatio(ratio):
    if ratio:
        return round(ratio, 4)
    else:
        return "N/A"


def pad(listOfRatios):
    while len(listOfRatios) < 10:
        # Dictionary to store padded ratios for one year (inside for loop so values persist as unique)
        somePaddedRatiosForOneYear = dict()

        somePaddedRatiosForOneYear["ticker"] = "N/A"
        somePaddedRatiosForOneYear["date"] = "N/A"

        # Profitability ratios
        somePaddedRatiosForOneYear["operatingProfitMargin"] = "N/A"
        somePaddedRatiosForOneYear["grossProfitMargin"] = "N/A"
        somePaddedRatiosForOneYear["netProfitMargin"] = "N/A"
        somePaddedRatiosForOneYear["returnOnAssets"] = "N/A"
        somePaddedRatiosForOneYear["returnOnEquity"] = "N/A"

        # Liquidity ratios
        somePaddedRatiosForOneYear["currentRatio"] = "N/A"
        somePaddedRatiosForOneYear["quickRatio"] = "N/A"

        # Leverage ratios
        somePaddedRatiosForOneYear["debtAssetRatio"] = "N/A"
        somePaddedRatiosForOneYear["debtEquityRatio"] = "N/A"
        somePaddedRatiosForOneYear["interestCoverageRatio"] = "N/A"

        # Efficiency ratios
        somePaddedRatiosForOneYear["inventoryTurnover"] = "N/A"
        somePaddedRatiosForOneYear["receivablesTurnover"] = "N/A"
        somePaddedRatiosForOneYear["payablesTurnover"] = "N/A"
        somePaddedRatiosForOneYear["assetTurnover"] = "N/A"

        # Market ratios
        somePaddedRatiosForOneYear["earningsPerShare"] = "N/A"
        somePaddedRatiosForOneYear["priceEarningsRatio"] = "N/A"
        somePaddedRatiosForOneYear["dividendYield"] = "N/A"

        # Add padded ratios of year to list of yearly ratios
        listOfRatios += somePaddedRatiosForOneYear

    return listOfRatios