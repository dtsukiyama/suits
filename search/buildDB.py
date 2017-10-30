import sqlite3
import pandas as pd
from pandas.io import sql



def createTable():
    string =  """ CREATE TABLE IF NOT EXISTS search_indexes (
                                        search_index text NOT NULL,
                                        columns text,
                                        string_columns,
                                        UNIQUE(search_index, columns, string_columns)
                                    ); """
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    conn.execute(string)
    conn.close()
       
def createIndex(new_index):

    sql = ''' INSERT OR IGNORE INTO search_indexes(search_index, columns, string_columns)
              VALUES(?,?,?) '''
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    conn.execute(sql, new_index)
    conn.commit()
    conn.close()
        
def returnIndex():
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    query_string = """select * from search_indexes"""
    return pd.read_sql(query_string,conn)

def getColumns(index_name, column):
    conn = sqlite3.connect('database/index.db', check_same_thread=False)
    query_string = '''select * from search_indexes where search_index ="{}"'''.format(index_name)
    data = pd.read_sql(query_string, conn)[column][0].split(',')
    data = [str(b) for b in data]
    return [" ".join(b.split()) for b in data]

