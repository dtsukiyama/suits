import pandas as pd
import spacy
nlp = spacy.load('en')


analysisSettings = {
   "analyzer" : {
      "default": {
        "type": "english"
      },
      "english_bigrams": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "standard",
            "lowercase",
            "bigram_filter"
          ]
      },
      "shingler":{
          "type":"custom",
          "tokenizer":"standard",
          "filter":["lowercase","shingle"]
        }  
        
    },
   "filter": {
     "bigram_filter": {
         "type": "shingle",
         "max_shingle_size": 3,
         "min_shingle_size": 2
     }}}




elasticsearch_dictionary = {'str':'string',
                            'float':'float',
                            'int':'int'}

def findEntIfString(doc):
    string_type = type(doc).__name__
    docstring = nlp(unicode(doc))
    isDate = [ent.label_ for ent in docstring.ents if ent.label_ == 'DATE']
    if not isDate:
        return elasticsearch_dictionary[string_type]
    elif len(isDate) > 1:
        return elasticsearch_dictionary[string_type]
    else:
        return 'date'
    
def findType(data):
    """
    Designate data types
    """
    type_dict = {}
    for key in data.keys():
        type_dict[key] = findEntIfString(data[key])
    return type_dict

def findStrings(data):
    data = data.head(1).to_dict(orient='records')[0]
    return [a for a, b in findType(data).iteritems() if b == 'string']

def stringAnalyzer(data, key, analyzer_type):
    """
    Analyze string variables and apply type and analyzer
    """
    if data[key] == 'string':
        analyzer = {'type':data[key]}
        analyzer['analyzer'] = analyzer_type
        return analyzer
    else:
        return {'type':data[key]}

def buildProperties(dataframe, analyzer_type):
    """
    Args: uploaded dataframe
    Returns: designate variable datatypes
    """
    data = dataframe.head(1).to_dict(orient='records')[0]
    data = findType(data)
    properties = {}
    for key in data.keys():
        properties[key] = stringAnalyzer(data, key, analyzer_type)
    return properties
    
    
def buildMapping(dataframe, analyzer_type):
    """
    Args: uploaded dataframe
    Returns: variable mappings for Elasticsearch indexing
    """
    mappingSettings = {
       "doc": {
            "properties":  buildProperties(dataframe, analyzer_type)
                    }
                }       
            
    return mappingSettings, analysisSettings

