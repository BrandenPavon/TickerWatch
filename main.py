import yfinance as yf
import json
import os
from flask import Flask, session
from flask import render_template, send_from_directory
from datetime import datetime, timezone
app = Flask(__name__)

class TickerData:

    def __init__(self):
        self.tickers = [] # string list holding individual tickers to watch
        self.portfolios = [] # string list holding portfolio to watch
        self.alltickersdaily = {} # dictionary storing all tickers info
        self.portfoliodaily= {} # dictionary storing all tickers info
        with open("config.json", "r") as f:
            data = json.load(f)

        self.tickers = data["tickers"]

        # test code
        for ticker in self.tickers:
            if ticker in self.alltickersdaily:
                continue
            else:
                self.alltickersdaily[ticker] = self.get_pct_change(yf.Ticker(ticker).info)
            print(ticker)


        self.portfolios = data["portfolios"]

        # test code
        for name, positions in self.portfolios.items():
            self.portfoliodaily[name] = 0
            for position in positions:
                print(position["ticker"])
                print(position["allocation"])
                if position["ticker"] in self.alltickersdaily:
                    pass
                else:
                    self.alltickersdaily[position["ticker"]] = self.get_pct_change(yf.Ticker(position["ticker"]).info)
                self.portfoliodaily[name] += self.alltickersdaily[position["ticker"]] * position["allocation"]
        print(self.portfoliodaily)

            

    def get_pct_change(self, ticker_info):
        prev = float(ticker_info["previousClose"])
        # try regularMarketPrice first, fallback to bid
        current = None
        if "regularMarketPrice" in ticker_info and ticker_info["regularMarketPrice"] is not None:
            current = float(ticker_info["regularMarketPrice"])
        else:
            # fallback to bid (if available)
            current = float(ticker_info.get("bid", prev))
        return (current - prev) / prev


@app.route("/")
def index():
    mydata = TickerData()
    return render_template("index.html", data_tickers=mydata.tickers, data_portfolios=mydata.portfolios, data_alltickersdaily=mydata.alltickersdaily, data_portfoliodaily = mydata.portfoliodaily );

if __name__ == "__main__":
    app.run()

