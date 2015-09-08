from flask import Flask, render_template, request, redirect, url_for, Markup
import requests
import simplejson as json
import pandas as pd
#from pandasql import sqldf
import numpy as np
from collections import OrderedDict
from bokeh.charts import TimeSeries
from bokeh.embed import components
from bokeh.resources import CDN

app = Flask(__name__)
#app.secret_key = 'R(f\x95>\xe5]J\xbfD\x9b\x80\xcf35?\xbcD\xe7\xb1\x1c\xbcr\xda'



@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']

        features = request.form.getlist('features')
        comma_separated = ','.join(features)

        #return redirect( url_for('graph', ticker=ticker, features=features) )
        return redirect( url_for('graph', ticker=ticker, features=comma_separated) )

    # the code below is executed if the request method was GET
    return render_template('index.html')

#@app.route('/graph/<ticker>/<features>')
#def graph(ticker, features):
@app.route('/graph')
def graph():
    ticker = request.args.get('ticker')
    features = request.args.get('features').split(',')

    response = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'/data.json') # , params = '')

    if response.status_code >= 200 and response.status_code <=209:
        # actually, much easier to do this with data.csv:
        # ticker_df = pd.read_csv(response.text, parse_dates='Date')
        #     well, just for practice...
        dataset_data = json.loads(response.text)['dataset_data']
        n_rows = len(dataset_data['data'])
        ticker_df =  pd.DataFrame( index=np.arange(0,n_rows), columns=dataset_data['column_names'] )
        for i in np.arange(0,n_rows):
            ticker_df.loc[i] = dataset_data['data'][i]
        ticker_df['Date'] = pd.to_datetime(ticker_df['Date'])

        xyvalues_dict = OrderedDict( Date=ticker_df['Date'] )
        PALETTE = []
        if 'Close' in features:
            xyvalues_dict[ticker+' Close'] = ticker_df['Close']
            PALETTE.append('Blue')
        if 'Adj. Close' in features:
            xyvalues_dict[ticker+' Adj. Close'] = ticker_df['Adj. Close']
            PALETTE.append('Orange')
        if 'Volume' in features:
            xyvalues_dict[ticker+' Volume'] = ticker_df['Volume']
            PALETTE.append('Green')

        if not PALETTE:
            return redirect('/error_quandle')

        xyvalues = pd.DataFrame( xyvalues_dict )

        TOOLS = 'pan,wheel_zoom,box_zoom,reset,save'

        ts = TimeSeries( xyvalues,
                         index = 'Date',
                         title = 'Data from Quandle WIKI set',
                         legend = True,
                         tools = TOOLS,
                         palette = PALETTE )

        script, div = components(ts)
        return render_template( 'graph.html',
                                ticker = ticker,
                                scr = script,
                                div = div )

    # the code below is executed if requests.get failed
    return redirect('/error_quandle')

@app.route('/error_quandle')
def error_quandle():
    return render_template('error_quandle.html')

if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=33507, debug=True)
    app.run(host='0.0.0.0', port=33507)
