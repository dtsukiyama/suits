def processForecast(dataframe):
    dataframe['date'] = dataframe['ds'].dt.strftime('%Y-%m-%d')
    dates = [str(b) for b in dataframe['date']]
    predictions = [b for b in dataframe['prediction']]
    lower = [b for b in dataframe['prediction_lower_bound']]
    upper = [b for b in dataframe['prediction_upper_bound']]
    monthly_forecast =[['month','prediction', 'prediction lower bound','prediction upper bound']]
    monthly_forecast = monthly_forecast + [list(a) for a in zip(dates, predictions, lower, upper)]
    return monthly_forecast
