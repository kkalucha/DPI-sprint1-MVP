from flask import Flask, render_template, request, jsonify, Response
import os
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import base64
import numpy as np
import pandas as pd
import pandas_datareader.data as web
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User

def portfolio(tickers,weights,backtest_window="2019-09-04",benchmark="SPY"):
    if weights.sum()!=1:
        print("Incorrect Weight Vector!")
        return -202,-202,-202
    if len(weights)!=len(tickers):
        print("Unmatched Dimensions!")
        return -203,-203,-203
    data=pd.DataFrame()
    bench=web.DataReader(benchmark, 'yahoo',start=backtest_window)["Close"]
    bench=bench[1:]/bench[0]
    for stock_ticker in tickers:
        data[stock_ticker]=web.DataReader(stock_ticker, 'yahoo',start=backtest_window)["Close"]
        print(".", end ="") 
    data_pct=data.pct_change()[1:]
    daily_portfolio_return=np.dot(data_pct,weights)
    mean_return=data_pct.mean()
    covariance_matrix=data_pct.cov()
    
    equity_curve=np.cumprod(daily_portfolio_return+1)
    ec=pd.Series(equity_curve,index=bench.index)
    fig=plt.figure()
    plt.plot(ec,label="Equity_Curve")
    plt.plot(bench,label="Benchmark")
    plt.xlabel("Day")
    plt.ylabel("Cummulative Percentage Return")
    plt.title("Portfolio Equity Curve")
    plt.legend()
    png_output = BytesIO()
    plt.savefig(png_output, format='png')
    png_output.seek(0)
    my_base64_jpgData = base64.b64encode(png_output.read())
    return daily_portfolio_return,mean_return,covariance_matrix,my_base64_jpgData

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')
    
@app.route('/createuser', methods=['POST'])
def createuser():
    json_data = request.get_json()
    username_ = json_data['Datum']['username']
    password_ = json_data['Datum']['password']
    if (User.query.filter_by(username = username_).count() > 0):
        return jsonify({'response' : 'user already exists'})
    user = User(username_, password_)
    db.session.add(user)
    db.session.commit()
    return jsonify({'response' : 'user created: ' + username_})

@app.route('/login', methods=['GET'])
def login():
    json_data = request.get_json()
    username_ = json_data['Datum']['username']
    password_ = json_data['Datum']['password']
    user = User.query.filter_by(username = username_).first()
    if (user.password == password_):
        return "success!! logged in"
    else:
        return "failure. does the user exist and is the password correct?"

@app.route('/plot', methods=['POST'])
def plot():
    json_data = request.get_json()
    weights_float = [ float(x) for x in json_data['Datum']['weights'] ]
    weights = np.asarray(weights_float)
    tickers = np.asarray(json_data['Datum']['tickers'])
    daily_portfolio_return, mean_return, covariance_matrix, fig = portfolio(tickers, weights, backtest_window="2019-09-04",benchmark="SPY")
    return jsonify({'b64encoded' : fig.decode('ascii')})
    return jsonify({'b64encoded' : weights[0]})

if __name__ == '__main__':
    app.run()