import sqlite3
import pandas as pd
from pandas.io import sql


def createTable():
    string =  """ CREATE TABLE IF NOT EXISTS search_indicies (
                                        search_index text NOT NULL,
                                        text text,
                                        terms text,
                                        entity_type text,
                                        UNIQUE(search_index, text)
                                    ); """
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    conn.execute(string)
    conn.close()
    
def createIndex(new_index):
    sql = ''' INSERT OR IGNORE INTO search_indicies(search_index, text, terms, entity_type)
              VALUES(?,?,?,?) '''
    conn = sqlite3.connect('database/index.db', check_same_thread=False) 
    conn.execute(sql, new_index)
    conn.commit()
    conn.close()
    
def returnIndex():
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    query_string = """select * from search_indicies"""
    return pd.read_sql(query_string,conn)

def getColumns(index_name, column):
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    query_string = '''select * from search_indicies where search_index ="{}"'''.format(index_name)
    data = pd.read_sql(query_string, conn)[column][0].split(',')
    data = [str(b) for b in data]
    return [" ".join(b.split()) for b in data][0]

def updateTerms(terms, index_name):
    terms = ",".join(terms)
    sql = ''' UPDATE search_indicies SET terms=? where search_index ="{}"'''.format(index_name)
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    conn.execute(sql, [terms])
    conn.commit()
    conn.close()
    
def updateEntity(entity, index_name):
    sql = ''' UPDATE search_indicies SET entity_type=? where search_index ="{}"'''.format(index_name)
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    conn.execute(sql, [entity])
    conn.commit()
    conn.close()
    
def getIndex(index_name):
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    query_string = '''select * from search_indicies where search_index ="{}"'''.format(index_name)
    return pd.read_sql(query_string,conn).to_dict(orient = 'records')[0]