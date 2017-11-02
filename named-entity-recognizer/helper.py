import pandas as pd
import lxml.html
import re

def removeNonAscii(data):
    return "".join(i for i in data if ord(i)<128)

def lxmlProcess(document):
    page = lxml.html.document_fromstring(document)
    page = page.cssselect('body')[0].text_content()
    return " ".join(page.replace('\n', ' ').replace('\r', ' ').lower().split())

def sentenceConversion(dataframe, column, splitter):
    dataframe[column] = [str(b) for b in dataframe[column]]
    dataframe[column] = dataframe[column].apply(lxmlProcess)
    if splitter == "None":
        return dataframe.reset_index().rename(columns={'index':'id'})
    else:
        sentences = (' '.join(dataframe[column])).lower().split(splitter)
        sentences = filter(None, sentences)
        sentences = list(set(sentences))
        sentences = [b.lstrip() for b in sentences]
        sentences = [str(removeNonAscii(b)) for b in sentences]
        sentences = [b.replace('-', ' ') for b in sentences]
        return pd.DataFrame({column:sentences}).reset_index().rename(columns={'index':'id'})
    

