from elasticsearch import Elasticsearch
from elasticsearch import helpers
from collections import Counter
from mapping import buildMapping

import requests
import pandas as pd
import re
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
res = requests.get('http://localhost:9200')

def deleteIndex(index_name):
    es.indices.delete(index=index_name, ignore=[400, 404])
    
def searchQuery(query, index_name, fields):
    results = es.search(index=[index_name], 
               body={'query': {'multi_match': { 'query': query, 
                                                'fields': fields,
                                                'type': 'cross_fields'
                                                }
                                },
                                'size': 25
                    })
    return results['hits']['hits']

def batch_index(dictionary, batch_size):
    """
    Get number of batches
    """
    batch_size = batch_size
    num_batches = len(dictionary)/batch_size
    if len(dictionary)%batch_size != 0:
        #then there's an additional partial batch to account for
        num_batches += 1  
    return num_batches

def buildBatchDict(documents, index_name):
    """
    Build dictionary batches that will appended to json to create data batches
    """
    doc_keys = documents[0].keys()
    json_docs = []
    for doc in documents:
        doc_short = {}
        for key in doc_keys:
            doc_short[key] = doc[key]
        addCmd = {"index": {"_index": index_name, "_type": "doc", "_id": doc_short["id"]}}
        json_docs.append(json.dumps(addCmd))
        json_docs.append(json.dumps(doc_short))
    return json_docs

def create_batches(dictionary, batch_size, index_name):
    """
    Create batches of data for indexing
    """
    num_batches = batch_index(dictionary, batch_size)
    batches = []
    for batch_num in xrange(num_batches):
        docs = dictionary[batch_num*batch_size:(batch_num+1)*batch_size]
        json_docs = buildBatchDict(docs, index_name)
        batches.append("\n".join(json_docs)+"\n")
    return batches

def batchReindex(batch_size, analysisSettings={}, mappingSettings={}, 
                  Dict={}, index_name = "index_name"):
    
    elasticSearchUrl = "http://localhost:9200"
    batches = create_batches(Dict, batch_size, index_name)
    settings = { 
        "settings": {
            "number_of_shards": 1, 
            "index": {
                "analysis" : analysisSettings, 
            }}}

    if mappingSettings:
        settings['mappings'] = mappingSettings 

    resp = requests.delete("http://localhost:9200/" + str(index_name)) 
    resp = requests.put("http://localhost:9200/" + str(index_name), data=json.dumps(settings))
    print("batch indexing...")
    for batch in batches:
        resp = requests.post(elasticSearchUrl + "/_bulk", data=batch)
    print("done")
    

def selectBatchSize(dataframe):
    """
    Select a good batch size. Setting the max to 50000, batches of 100000 tend to give connection errors.
    """
    threshold = int(len(dataframe)*.10)
    if threshold <= 50000:
        return threshold
    else:
        return 50000

def buildIndex(dataframe, index_name, analyzer_type):
    """
    Create settings and index data into Elasticsearch local cluster
    """
    dataframe['id'] = dataframe.index
    mappingSettings, analysisSettings = buildMapping(dataframe, analyzer_type)
    dataframe = json.loads(dataframe.to_json(orient='records'))
    batchReindex(selectBatchSize(dataframe), analysisSettings=analysisSettings, 
                 mappingSettings=mappingSettings, 
                 Dict = dataframe, index_name = index_name)
    
    