from flask import Flask, render_template, request, redirect
from wtforms import Form, FloatField, validators
from datetime import date
import sys
import pandas as pd
import simplejson as json
import quandl
import pandas as pd
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.util.string import encode_utf8

today = pd.to_datetime(str(date.today()))
ago = today - pd.DateOffset(months=3)
ago = str(ago.to_period('D'))
today = str(today.to_period('D'))

def plotStockPrice(symbol,plotOptions=[]):
    # ['ticker', 'date', 'open', 'close', 'adj_open', 'adj_close'] 
    cols = ['ticker', 'date'] + plotOptions
    tmp=quandl.get_table('WIKI/PRICES',\
                       qopts = { 'columns': cols },\
                         ticker = symbol)
    if(tmp.empty):
        return("","")

    p = figure(plot_width=800,\
               plot_height=300,\
               x_axis_type="datetime",\
               title="{:s} stock price".format(symbol))
    p.title.text_color = "black"
    p.title.text_font = "arial"

    for label,color in zip(plotOptions,Spectral4):
        p.line(tmp['date'],\
           tmp[label],\
           color=color,\
           legend=label,\
           alpha=0.8,\
           line_width=5)
    
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Stock price"
    p.legend.click_policy="hide"
    script,div = components(p)
    return(script,div)

app = Flask(__name__)

class InputForm(Form):
    stockSymbol = FloatField(validators=[validators.InputRequired()])

figdata = None
import os
try:
    quandl.ApiConfig.api_key = os.environ["QUANDL_KEY"]
except:
    print("quandl key not defined")
    print("Failing as loudly as possible")
    print("DEFINE QUANDL_KEY BEFORE RERUNNING")
    raise

# Index page, no args
@app.route('/', methods=['GET','POST'])
def index():
  p = None
  form = InputForm(request.form)
  if(request.method == 'POST'):
      
    # Get checked options
    plotOptions = request.form.getlist('plotOptions')
    options = [False,False,False,False]
    options[0] = ("close" in plotOptions)
    options[1] = ("adj_close" in plotOptions)
    options[2] = ("open" in plotOptions)
    options[3] = ("adj_open" in plotOptions)

    # Get stock symbol
    stockSymbol = request.form['stockSymbol']
    script,div = plotStockPrice(stockSymbol,plotOptions)
    if(script != ""):
      return(render_template("index.html",\
                             form=form,\
                             oClose=options[0],\
                             oAdjClose=options[1],\
                             oOpen=options[2],\
                             oAdjOpen=options[3],\
                             options=options,\
                             script=script,\
                             div=div))
    else:
      return(render_template("index.html",\
                             form=form,\
                             oClose=options[0],\
                             oAdjClose=options[1],\
                             oOpen=options[2],\
                             oAdjOpen=options[3],\
                             options=options,\
                             status="Symbol not found"))
  else:
    return(render_template("index.html",\
                           form=form,\
                           oClose=True,\
                           oAdjClose=False,\
                           oOpen=False,\
                           oAdjOpen=False,\
                           status=""))
  return("OK")

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
