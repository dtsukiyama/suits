import pandas as pd
import pickle
import numpy as np
import os
import re
import timeit
import spacy

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for, session, send_file
from collections import OrderedDict
from werkzeug.utils import secure_filename
from mapping import findType
from mapping import findStrings
from helper import sentenceConversion
from buildDB import createIndex, returnIndex, updateTerms, getColumns, updateEntity, getIndex
from elastic import buildIndex
from ner import entityTraining
from validator import entValidator

from flask_uploads import UploadSet, configure_uploads, DATA, UploadNotAllowed

nlp = spacy.load('en')

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
    # get text columns
    text_columns = findStrings(pd.read_csv('data/'+data_name))
    return render_template("settings.html", menu=menu, text_columns=text_columns)


@app.route('/build_model', methods=['GET','POST'])
def buildModel(): 
    error=""
    if request.method == 'POST': 
        data = request.form['data-verification']
        text_column = request.form['text-column']
        splitter = request.form['splitter']
        index_name = data.split('.')[0]
        dataframe = pd.read_csv('data/'+data, usecols = [text_column])
        dataframe = sentenceConversion(dataframe, text_column, splitter)
        createIndex((index_name, text_column, 'None','None'))
        buildIndex(dataframe, index_name, 'english_bigrams')
        menu = returnIndex()['search_index'].tolist()
        return render_template("train.html", menu = menu)

@app.route('/train', methods=['POST'])
def train():
    index = request.form['data-index']
    entity_name = request.form['entity']
    iterations = request.form['iterations']
    uploaded_terms = request.files['terms'].read().replace('\n', '').split(',')
    updateTerms(uploaded_terms, index)
    updateEntity(entity_name, index)
    samples = request.form['Number']
    text_column = getColumns(index,'text')
    model = entityTraining(index, text_column)
    model.buildNer(uploaded_terms, samples, int(iterations), entity_name)
    models = os.listdir("models/")
    return render_template("extend.train.html", models=models)

@app.route('/test', methods=['POST'])
def test():
    text = request.form['query']
    model = request.form['model']
    indexLookUp = getIndex(model)
    terms = [str(b) for b in indexLookUp['terms'].split(',')]
    entity = str(indexLookUp['entity_type'])
    ner = spacy.load('en', path='models/'+ model)
    ner.entity.add_label(entity)
    ent_model = entValidator(entity, terms, ner)
    results = ent_model.displayTerms(text)
    models = os.listdir("models/")
    return render_template("extend.train.html", results=results, models=models)

@app.route('/test', methods=['POST'])
def buildPip():
    return render_template("extend.train.html")

@app.route('/', methods=['GET'])
def main_page():
    return render_template("index.html")   

if __name__ == '__main__':
    app.run(debug=True)