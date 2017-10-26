
import pandas as pd
import pickle
import numpy as np
import os

from forecast import forecastData
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for, session, send_file
from collections import OrderedDict
from werkzeug.utils import secure_filename

from flask_uploads import UploadSet, configure_uploads, DATA, UploadNotAllowed

app = Flask(__name__)

data = UploadSet('data', DATA)
app.config['UPLOADED_DATA_DEST'] = 'data/'
configure_uploads(app, data)
    
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST' and 'data' in request.files:
        filename = data.save(request.files['data'])
    datafiles = os.listdir("data/")
    menu = datafiles
    return render_template("forecast.html", menu=menu)


@app.route('/model_forecast', methods=['GET','POST'])
def modelForecast(): 
    error=""
    if request.method == 'POST': 
        df = request.form['data-verification']
        print(df)
        periods = request.form['Number']
        print(type(periods))
        model, table = forecastData(df, int(periods))
        menu = os.listdir("predictions/")
        return render_template("model_forecast.html", model = model, table = table, menu = menu)
    

@app.route('/download', methods=['GET','POST']) 
def downloadPredictions():
    if request.method == 'POST':
        data = request.form['data-download']
        print(data)
        return send_file('predictions/'+ data,
                         mimetype='text/csv',
                         attachment_filename=data,
                         as_attachment=True)

@app.route('/', methods=['GET'])
def main_page():
    return render_template("index.html")   

if __name__ == '__main__':
    app.run(debug=True)
