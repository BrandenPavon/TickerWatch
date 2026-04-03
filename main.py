import yfinance as yf
import pandas as pd
import pytz
import json
import os
from flask import Flask
from flask import render_template, send_from_directory
from datetime import datetime
app = Flask(__name__)

with open("config.json", "r") as f:
    data = json.load(f)

class TickerData:
    debug = False
    def __init__(self, debug=debug):
        self.tickers = [] # string list holding individual tickers to watch
        self.portfolios = [] # string list holding portfolio to watch
        self.alltickers = {} # dictionary storing all tickers info

        self.alltickersdataframe = {} # dictionary storing all tickers info

        self.alltickersdata = {} # dictionary storing all tickers info

        self.portfoliodata= {} # dictionary storing all tickers info
        global data
        self.debug = debug
        self.tickers = data["tickers"]

        # download ticker data
        for ticker in self.tickers:
            if(self.debug == True): print(ticker)
            if ticker in self.alltickers:
                pass
            else:
                self.alltickers[ticker] = 0

        self.portfolios = data["portfolios"]

        # download ticker data
        for name, positions in self.portfolios.items():
            if(self.debug == True): print(name, positions)
            for position in positions:
                if(self.debug == True): print(position["ticker"])
                if(self.debug == True): print(position["allocation"])
                if position["ticker"] in self.alltickers:
                    pass
                else:
                    self.alltickers[position["ticker"]] = 0

        self.alltickersdataframe = self.get_bulk_ticker_data(list(self.alltickers.keys()))
        self.calculate_pct_changes()
        self.calculate_portfolio_pct_changes()
         
                

    def get_bulk_ticker_data(self, tickers):
        df = yf.download(
            tickers,
            start=(datetime.now(pytz.timezone('America/Los_Angeles')) - pd.DateOffset(years=1)).date(),
            end=datetime.now(pytz.timezone('America/Los_Angeles')),
            progress=False
        )
        return df           
    def calculate_pct_changes(self):
        for ticker in self.alltickers:
            # Extract close prices for this ticker from the MultiIndex dataframe
            close = self.alltickersdataframe["Close"][ticker]

            now = datetime.now(pytz.timezone('America/Los_Angeles'))

            # YTD: from first trading day of this year to latest
            ytd = close.loc[str(now.year):]
            ytd_pctchange = (ytd.iloc[-1] / ytd.iloc[0]) - 1

            # Month: from first trading day of current month to latest
            month_pctchange = (close.iloc[-1] / close.iloc[-22]) - 1

            # 1 Year: rolling 365 days back from today
            one_year_ago = (now - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
            year = close.loc[one_year_ago:]
            year_pctchange = (year.iloc[-1] / year.iloc[0]) - 1

            # Day: (close - open) / open for the latest trading day
            latest_open = self.alltickersdataframe["Open"][ticker].iloc[-1]
            latest_close = self.alltickersdataframe["Close"][ticker].iloc[-1]
            close = self.alltickersdataframe["Close"][ticker]
            if len(close) >= 2:
                day_pctchange = (close.iloc[-1] / close.iloc[-2]) - 1
            else:
                day_pctchange = 0.0

            self.alltickersdata[ticker] = {
                "day_pctchange": day_pctchange,
                "month_pctchange": month_pctchange,
                "ytd_pctchange": ytd_pctchange,
                "year_pctchange": year_pctchange
            }
    def calculate_portfolio_pct_changes(self):
        for name, positions in self.portfolios.items():
            
            self.portfoliodata[name] = {
                "day_pctchange": 0,
                "month_pctchange": 0,
                "ytd_pctchange": 0,
                "year_pctchange": 0
            }

            for position in positions:
                if(self.debug == True): print(position["ticker"])
                if(self.debug == True): print(position["allocation"])
                self.portfoliodata[name]["day_pctchange"] += self.alltickersdata[position["ticker"]]["day_pctchange"] * position["allocation"] 
                self.portfoliodata[name]["month_pctchange"] += self.alltickersdata[position["ticker"]]["month_pctchange"] * position["allocation"] 
                self.portfoliodata[name]["ytd_pctchange"] += self.alltickersdata[position["ticker"]]["ytd_pctchange"] * position["allocation"] 
                self.portfoliodata[name]["year_pctchange"] += self.alltickersdata[position["ticker"]]["year_pctchange"] * position["allocation"]
        
    
@app.route("/")
def index():
    mydata = TickerData(debug=False)
    
    return render_template("index.html",
        data_alltickersdata=mydata.alltickersdata,
        data_portfolios=mydata.portfoliodata,
        watch_tickers=mydata.tickers
    )

@app.route("/allocations")
def allocations():
    mydata = TickerData(debug=False)
    return render_template("allocations.html",
        data_alltickersdata=mydata.alltickersdata,
        data_portfolios=mydata.portfoliodata,
        watch_tickers=mydata.tickers
    )
@app.route('/favicon.ico')

def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/config.json')
def configjson():
    return send_from_directory(app.root_path, 'config.json', mimetype='application/json')

if __name__ == "__main__":
    app.run()

