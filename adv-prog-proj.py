import json
from bson import json_util
from pymongo import MongoClient
import bottle

connection = MongoClient('localhost', 27017)
db = connection['market']
collection = db['stocks']

html_template = "<!DOCTYPE html><html><head><title>CRUD App</title><head/><body><h1>JSON Response</h1><p>REPLACE_HERE</p><p><a href=\"http://localhost:8080/index\">Go back</a></p><body/></html>"

BASE_URL = "/stocks/api/v1.0/"

@bottle.route(BASE_URL + "createStock/", method="POST")
def createStock():
    ticker = bottle.request.forms.get("ticker")
    document = json_util.loads(bottle.request.forms.get("json-payload"))
    
    # Sets the correct Ticker for the new stock.
    document["Ticker"] = ticker
    
    try:
        collection.insert_one(document)
        bottle.response.status = 200
        with open("./success.html", "r") as f:
            data = f.read()
        return data
    except Exception as e:
        bottle.response.status = 500
        with open("./failure.html", "r") as f:
            data = f.read()
        return data


@bottle.route(BASE_URL + "getStock/", method="POST")
def getStock():
    ticker = bottle.request.forms.get("ticker")

    try:
        res = collection.find_one({"Ticker": ticker})
        bottle.response.status = 200
        return html_template.replace("REPLACE_HERE", json_util.dumps(res))
    except Exception as e:
        bottle.response.status = 404
        with open("./failure.html", "r") as f:
            data = f.read()
        return data

@bottle.route(BASE_URL + "updateStock/", method="POST")
def updateStock():
    ticker = bottle.request.forms.get("ticker")
    document = json_util.loads(bottle.request.forms.get("json-payload"))

    try:
        res = collection.update_one({"Ticker" : ticker}, {"$set" : document}, upsert=False)
    except:
        bottle.response.status = 404
        with open("./failure.html", "r") as f:
            data = f.read()
        return data

    bottle.response.status = 200
    with open("./success.html", "r") as f:
        data = f.read()
    return data

@bottle.route(BASE_URL + "deleteStock/", method="POST")
def deleteStock():
    ticker = bottle.request.forms.get("ticker")

    try:
        res = collection.delete_one({"Ticker": ticker})
        bottle.response.status = 200
        with open("./success.html", "r") as f:
            data = f.read()
        return data
    except:
        bottle.response.status = 400
        with open("./failure.html", "r") as f:
            data = f.read()
        return data
    
@bottle.route(BASE_URL + "stockReport/", method="POST")
def stockReport():
    tickers = bottle.request.forms.get("tickers").split(",")
    print(tickers)

    res = {}
    try:
        for t in tickers:
            res[t] = collection.find_one({"Ticker": t})
        bottle.response.status = 200
        return html_template.replace("REPLACE_HERE", json_util.dumps(res))
    except Exception as e:
        bottle.response.status = 404
        with open("./failure.html", "r") as f:
            data = f.read()
        return data
    
@bottle.route(BASE_URL + "industryReport/", method="POST")
def industryReport():
    industry = bottle.request.forms.get("industry")
    industry = industry.replace("%20", " ")
    industry = industry.replace("%26", "&")
    industry = industry.replace("%2E", ".")
    
    try:
        res = collection.find({"Industry": industry})
        res = res.sort([("Performance (Year)", -1)]).limit(5)
        bottle.response.status = 200
        return html_template.replace("REPLACE_HERE", json_util.dumps(res))
    except Exception as e:
        print(e)
        bottle.response.status = 404
        with open("./failure.html", "r") as f:
            data = f.read()
        return data

@bottle.route(BASE_URL + "portfolio/", method="POST")
def portfolio():
    company_name = bottle.request.forms.get("company")
    company_name = company_name.replace("%20", " ")
    company_name = company_name.replace("%26", "&")
    company_name = company_name.replace("%2E", ".")

    try:
        res = collection.find_one({"Company": company_name})
        industry = res["Industry"]
        res = collection.find({"Industry": industry})
        bottle.response.status = 200
        return html_template.replace("REPLACE_HERE", json_util.dumps(res))
    except Exception as e:
        print(e)
        bottle.response.status = 404
        with open("./failure.html", "r") as f:
            data = f.read()
        return data

@bottle.route("/index", method="GET")
def index():
    with open("./index.html", "r") as f:
        data = f.read()
    return data

def main():
  bottle.run(host="localhost", port=8080)

main()
