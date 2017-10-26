import pandas as pd
import numpy as np
from fbprophet import Prophet
from helper import processForecast

import spacy
nlp = spacy.load('en')

fields = {'str':'string',
          'int':'int',
          'float':'float'}

def formatDates(data):
    data = list(zip([b for b in data['year']],
                    [b for b in data['month']]))
    return ['new Date({},{})'.format(a, b) for a, b in data]

def findDate(doc):
    docstring = nlp(unicode(doc))
    isdate = [ent.label_ for ent in docstring.ents if ent.label_ == 'DATE']
    if len(isdate) == 0:
        return fields[str(type(doc).__name__)]
    else:
        return isdate[0].lower()
    
def findType(dictionary):
    type_dict = {}
    for key in dictionary.keys():
        type_dict[key] = findDate(dictionary[key])
    return type_dict

def buildType(dataframe):
    data = dataframe.head(1).to_dict(orient='records')[0]
    data = findType(data)
    ds = [key for key, value in data.iteritems() if value == 'date'][0]
    y = [key for key, value in data.iteritems() if value == 'float' or value == 'int'][0]
    dataframe = dataframe.rename(columns={ds:'ds', y:'y'})
    return dataframe

def forecastData(name, periods):
    dataframe = pd.read_csv('data/' + name)
    dataframe = buildType(dataframe)
    m = Prophet()
    m.fit(dataframe)
    future = m.make_future_dataframe(periods=periods, freq = 'M')
    forecast = m.predict(future)
    forecast = forecast.rename(columns={'yhat':'prediction','yhat_lower':'prediction_lower_bound',
                                        'yhat_upper':'prediction_upper_bound'})
    monthly_forecast = processForecast(forecast)
    forecast_table = forecast[['date','prediction', 'prediction_lower_bound',
                               'prediction_upper_bound']].sort_values('date', ascending=False).round().to_html()
    forecast[['date','prediction', 'prediction_lower_bound',
                               'prediction_upper_bound']].to_csv('predictions/prediction_'+name, index = False)
    return monthly_forecast, forecast_table
