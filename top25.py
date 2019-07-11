#!/usr/bin/env python
# coding: utf-8

# In[4]:


#Import Dependencies
import pandas as pd
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from pprint import pprint
import json
import csv, sqlite3
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect, desc, and_, or_
import datetime
from highcharts import Highchart


#Filter dataframe with selected 10 airports and airlines
airports=["ATL", "BOS", "DAL", "DEN", "FLL", "JFK", "LAS", "LAX", "PDX", "SFO"]
airlines=["DL", "WN","UA","B6","AS","AA","OO","F9","EV","HA"]

month_conv = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
airline_conv = {}

#Read CSV file to convert into dataframe
path = "Resources/data/select_top10.csv"
csvdf = pd.read_csv(path)

ontime_data = csvdf[csvdf.Origin.isin(airports) & csvdf.Dest.isin(airports) &
                    csvdf.IATA_Code_Operating_Airline.isin(airlines)]

# Clean data by dropping na data 
for column in ['Month', 'DOT_ID_Operating_Airline', 'Flight_Number_Operating_Airline',
               'OriginAirportID', 'DestAirportID', 'ArrDelayMinutes']:
    pd.to_numeric(ontime_data[column], errors='coerce')
    ontime_data = ontime_data.dropna(subset=[column])

airline_groups = ontime_data.groupby(
    ['IATA_Code_Operating_Airline', 'DOT_ID_Operating_Airline']
)['IATA_Code_Operating_Airline'].unique().to_dict().keys()  

# Push the filtered data into the database
engine = create_engine("sqlite:///Resources/data/ontime.sqlite")
Base = automap_base()
Base.metadata.create_all(engine)
Base.prepare(engine, reflect = True)

session = Session(bind=engine)    
ontime_data.to_sql(name='ontime', con=engine, if_exists='replace')

for item in list(airline_groups):
    airline_conv[item[0]] = item[1]

airport_conv = {}
airport_groups = ontime_data.groupby(['Origin', 'OriginAirportID'])['Origin'].unique().to_dict().keys()
for item in list(airport_groups):
    airport_conv[item[0]] = item[1]

# Setup ML
y = ontime_data["ArrDelayMinutes"] 
ontime_features = ["Month","DOT_ID_Operating_Airline", "OriginAirportID", "DestAirportID"]
X = ontime_data[ontime_features]  # features to help predict the data

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

ontimemodel = DecisionTreeRegressor(random_state=1)

ontimemodel.fit(train_X,train_y) # training the model


def doPredict(month, origin, dest):
    invalues = []
    for airline in airlines:
        if airline in airline_conv:
            #print(airline, airline_conv[airline])
            invalues.append([month_conv[month], airline_conv[airline], airport_conv[origin], airport_conv[dest]])

    # Gather data for rendering airline arrival delay metrics
    y = ontime_data["ArrDelayMinutes"]  # The prediction data

    print("Making predictions for the following 8 airlines:")
    print(invalues)
    print("The predictions are")

    val_predictions = {}
    for airline, invalue in zip(airlines, invalues):
        val_predictions[airline] = ontimemodel.predict([invalue])[0]

    return val_predictions


    
def doMean(month, origin, dest):
    val_means = []
    index = 0
    result_df = pd.DataFrame(columns=['Airline', 'Predicted Arrival Delay', 'Average Arrival Delay'])
    for invalue in invalues:
        airline_df = ontime_data.loc[(ontime_data['Month'] == invalue[0]) &
                                     (ontime_data['DOT_ID_Operating_Airline'] == invalue[1]) &
                                     (ontime_data['OriginAirportID'] == invalue[2]) &
                                     (ontime_data['DestAirportID'] == invalue[3])]
        if airline_df.shape[0] == 0:
           # print("Airline: {}, Delay prediction not available".format(airlines[index]))
            result_df.loc[index] = [airlines[index], "Not Available", "Not Available"]
        else:
            predictedDelay = ontimemodel.predict([invalue])[0]
            averageDelay = airline_df['ArrDelayMinutes'].mean(axis=0)
            #print("Airline: {}, Predicted delay: {} minutes, Average delay: {} minutes".format(
                #airlines[index], predictedDelay, averageDelay))
            result_df.loc[index] = [airlines[index], predictedDelay, averageDelay]
        index = index + 1
    result_df.sort_values(by=['Predicted Arrival Delay','Average Arrival Delay'], ascending=True)
    return result_df



def doPieChart(month, airline, origin, dest):
    select_df = ontime_data.loc[(ontime_data['Month'] == month_conv[month]) &
                                (ontime_data['DOT_ID_Operating_Airline'] == airline_conv[airline]) &
                                (ontime_data['OriginAirportID'] == airport_conv[origin]) &
                                (ontime_data['DestAirportID'] == airport_conv[dest])]

    charData = {}
    charData['CarrierDelay'] = int(select_df.loc[select_df['CarrierDelay'] > 0].count()['Month'])
    chartData['WeatherDelay'] = int(select_df.loc[select_df['WeatherDelay'] > 0].count()['Month'])
    chartData['NASDelay'] = int(select_df.loc[select_df['NASDelay'] > 0].count()['Month'])
    chartData['SecurityDelay'] = int(select_df.loc[select_df['SecurityDelay'] > 0].count()['Month'])
    chartData['LateAircraftDelay'] = int(select_df.loc[select_df['LateAircraftDelay'] > 0].count()['Month'])

    return charData

    # print(cd, wd, nd, sd, ld)

    # chart = Highchart(width=650, height=400)

    # data = [ {
    #     'name': "Carrier Delay",
    #     'y': cd,
    #     'sliced': True,
    #     'selected': True
    # }, {
    #     'name': "WeatherDelay",
    #     'y': wd
    # }, {
    #     'name': "NasDelay",
    #     'y': nd
    # }, {
    #     'name': "SecurityDelay",
    #     'y': sd
    # }, {
    #     'name': "LateAircraftDelay",
    #     'y': ld
    # }]
    
    # options = {
    #         'chart': {
    #         'plotBackgroundColor': 'grey',
    #         'plotBorderWidth': None,
    #         'plotShadow': False
            
    #     },
    #     'title': {
    #         'text': 'Delayed reasons split for the Year 2018'
    #     },
    #     'tooltip': {
    #         'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
    #     },
    # }

    # chart.set_dict_options(options)

    # chart.add_data_set(
    #     data, 'pie', 'Browser share', allowPointSelect=True,
    #             cursor='pointer',
    #             showInLegend=True,
    #             dataLabels={
    #                 'enabled': False,
    #                 'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
    #                 'style': {
    #                     'color': "(Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'"
    #                 }
    #             }
    #         )

    # chart.save_file()

print(doPredict("Apr", 'SFO', 'BOS'))
