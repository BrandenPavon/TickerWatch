import yfinance as yf
import pytz
import json
import os
from flask import Flask, session
from flask import render_template, send_from_directory
from datetime import datetime, timezone
app = Flask(__name__)

class TickerData:

    def __init__(self, debug=False):
        self.tickers = [] # string list holding individual tickers to watch
        self.portfolios = [] # string list holding portfolio to watch
        self.alltickersdaily = {} # dictionary storing all tickers info
        self.alltickersytd= {} # dictionary storing all tickers info
        self.portfoliodaily= {} # dictionary storing all tickers info
        self.portfolioytd = {} # dictionary storing all tickers info
        with open("config.json", "r") as f:
            data = json.load(f)

        self.tickers = data["tickers"]

        # test code
        for ticker in self.tickers:
            if(debug == True): print(ticker)
            if ticker in self.alltickersdaily:
                pass
            else:
                self.alltickersdaily[ticker] = self.get_pct_daily_change(yf.Ticker(ticker).info)
            if ticker in self.alltickersytd:
                pass
            else:
                self.alltickersytd[ticker] = self.get_pct_ytd_change(yf.Ticker(ticker).info)


        self.portfolios = data["portfolios"]

        # test code
        for name, positions in self.portfolios.items():
            self.portfoliodaily[name] = 0
            self.portfolioytd[name] = 0
            for position in positions:
                if(debug == True): print(position["ticker"])
                if(debug == True): print(position["allocation"])
                if position["ticker"] in self.alltickersdaily:
                    pass
                else:
                    self.alltickersdaily[position["ticker"]] = self.get_pct_daily_change(yf.Ticker(position["ticker"]).info)
                if position["ticker"] in self.alltickersytd:
                    pass
                else:
                    self.alltickersytd[position["ticker"]] = self.get_pct_ytd_change(yf.Ticker(position["ticker"]).info)

                self.portfoliodaily[name] += self.alltickersdaily[position["ticker"]] * position["allocation"]
                self.portfolioytd[name] += self.alltickersytd[position["ticker"]] * position["allocation"]
            print(name, self.portfolioytd[name])
        if(debug == True): print(self.portfoliodaily)

            

    def get_pct_daily_change(self, ticker_info):
        prev = float(ticker_info["previousClose"])
        # try regularMarketPrice first, fallback to bid
        current = None
        if "regularMarketPrice" in ticker_info and ticker_info["regularMarketPrice"] is not None:
            current = float(ticker_info["regularMarketPrice"])
        else:
            # fallback to bid (if available)
            current = float(ticker_info.get("bid", prev))
        return (current - prev) / prev
    def get_pct_ytd_change(self, ticker_info):
        df = yf.download(ticker_info["symbol"], start=datetime(datetime.now(pytz.timezone('America/Los_Angeles')).year,1,1).date(), end=datetime.now(pytz.timezone('America/Los_Angeles')), progress=False)
        close = df["Close"].squeeze()
        start = close.iloc[0]
        end = close.iloc[-1]
        pct = (end - start) / start * 100

        return pct

@app.route("/")
def index():
    mydata = TickerData(debug=False)
    return render_template("index.html", data_tickers=mydata.tickers, data_portfolios=mydata.portfolios, data_alltickersdaily=mydata.alltickersdaily, data_portfoliodaily = mydata.portfoliodaily );

@app.route("/allocations")
def allocations():
    mydata = TickerData(debug=False)
    return render_template("allocations.html", data_tickers=mydata.tickers, data_portfolios=mydata.portfolios, data_alltickersdaily=mydata.alltickersdaily, data_portfoliodaily = mydata.portfoliodaily );
@app.route('/favicon.ico')

def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/config.json')
def configjson():
    return send_from_directory(app.root_path, 'config.json', mimetype='application/json')

if __name__ == "__main__":
    print(yf.Ticker("SPY").info)
    app.run()

