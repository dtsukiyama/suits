import pandas as pd
import pickle
import numpy as np
import os
import re

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for, session, send_file
from collections import OrderedDict
from werkzeug.utils import secure_filename
from mapping import findType
from elastic import buildIndex, searchQuery
from buildDB import createIndex, returnIndex, getColumns
from mapping import findStrings

from flask_uploads import UploadSet, configure_uploads, DATA, UploadNotAllowed

app = Flask(__name__)

data = UploadSet('data', DATA)
app.config['UPLOADED_DATA_DEST'] = 'data/'
configure_uploads(app, data)

def cleanQuery(results, columns):
    results = [b['_source'] for b in results]
    data = []
    for result in results:
        col_data = []
        for col in columns:
            col_data.append(result[col])
        data.append(col_data)
    return data
       
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST' and 'data' in request.files:
        filename = data.save(request.files['data'])
        data_name = request.files['data'].filename
    datafiles = os.listdir("data/")
    menu = datafiles
    return render_template("settings.html", menu = menu)


@app.route('/build_model', methods=['GET','POST'])
def buildModel(): 
    error=""
    if request.method == 'POST': 
        data = request.form['data-verification']
        analyzer = request.form['analyzer']
        index_name = data.split('.')[0]
        dataframe = pd.read_csv('data/'+data)
        columns = ', '.join(dataframe.columns)
        string_columns = findStrings(dataframe)
        createIndex((index_name, columns, string_columns))
        buildIndex(dataframe, index_name, analyzer)
        menu = returnIndex()['search_index'].tolist()
        return render_template("search.html", menu = menu)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    index= request.form['data-index']
    results = searchQuery(query, index, getColumns(index,'string_columns'))
    columns = getColumns(index,'columns')
    results = cleanQuery(results, columns)
    menu = returnIndex()['search_index'].tolist()
    return render_template("extend.search.html", columns = columns, results = results, menu=menu)

@app.route('/', methods=['GET'])
def main_page():
    return render_template("index.html")   

if __name__ == '__main__':
    app.run(debug=True)