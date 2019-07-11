#!/usr/bin/env python
# coding: utf-8

import pandas as pd

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from pprint import pprint
from sklearn.linear_model import LinearRegression

from sqlalchemy.orm import Session
from sqlalchemy.orm import join
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, Float
from statistics import mean , StatisticsError


engine = create_engine("sqlite:///db/flight1.sqlite", connect_args={'check_same_thread': False})

conn = engine.connect()


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
AIRPORT_DETAILS = Base.classes.airport_details
DBIB_DETAILS = Base.classes.db1b_details
AIRLINES_DETAILS = Base.classes.airlines_details


# Create our session (link) from Python to the DB
session = Session(bind=engine)

DBIB_DETAILS_DF = pd.read_sql("select * from db1b_details", conn )


# "MARKET_FARE"  This is the value that I would like to Predict
y = DBIB_DETAILS_DF["MARKET_FARE"]


features = ["PASSENGERS","MARKET_MILES_FLOWN", "MARKET_DISTANCE"]


X = DBIB_DETAILS_DF[features]

# spliting the data into 80 - 20 parts

train_X, val_X, train_y, val_y = train_test_split(X, y, test_size=0.2, random_state=1)  


# ## DECISION TREE REGRESSOR

ticketmodel = DecisionTreeRegressor(random_state=0)

ticketmodel.fit(train_X,train_y) # tranining the model


# ## Predict Market fare

def predictMarketFare(qtr, origin, dest, airline):

    ### Ticket fare price prediction using DecisionTreeRegressor
    query = f"select PASSENGERS,MARKET_MILES_FLOWN,MARKET_DISTANCE from db1b_details where QUARTER='{qtr}' AND ORIGIN ='{origin}' AND DEST ='{dest}' AND REPORTING_CARRIER ='{airline}'"
    test_data = pd.read_sql(query, conn)
    test_X = test_data[features]
    try:
        val_predictions = ticketmodel.predict(test_X)
        mean_preds = mean(val_predictions)
        predfare = round(mean_preds)

    except ValueError:
    
    ### if there no rows for the selected value calculate the mean airfare for the selected airline. 

        query = f"select Market_fare from db1b_details where REPORTING_CARRIER ='{airline}'"
        airfare = pd.read_sql(query, conn)
        numMarket_fare = pd.to_numeric(airfare["MARKET_FARE"])
        mean_preds = mean(numMarket_fare)
        predfare = round(mean_preds)    

    return predfare

# predictMarketFare(3, "LAX", "FLL", "AA")

carriercodes = ["DL","WN","UA","B6","AS","AA","OO","F9","EV", "HA"]  ## used for loop
predfare = []
predotherairlines =[]
airlinenames = []
# predmean_df_new =pd.DataFrame([{'Airline_Name':[], 'Airline_Code':[],'Predicted_Average_Fare':[] }])

def predictallairfare(qtr, origin, dest, chosenairline):
    predmean_df_new =pd.DataFrame([{'Airline_Name':[], 'Airline_Code':[],'Predicted_Average_Fare':[] }])
    predfare.clear() ## clearing existing values in the list
    predotherairlines.clear()
    airlinenames.clear()
    for air in carriercodes: 
        try:
          mean_preds = predictMarketFare(qtr, origin, dest,air) 

          query = f"select AIRLINES_NAME from AIRLINES_DETAILS where AIRLINES_CODE ='{air}'"
          result = conn.execute(query)
          for row in result:
            airname = row['AIRLINES_NAME']

          predfare.append(mean_preds)
          predotherairlines.append(air)
          airlinenames.append(airname)
        except ValueError:
                 print(f"Prediction not available for {air}")
    
    if len(predmean_df_new.index) > 0:
        predmean_df_new = predmean_df_new.drop(['Airline_Name', 'Airline_Code','Predicted_Average_Fare'], axis=1)
    
    predmean_df_new =pd.DataFrame({"Airline_Name":airlinenames,"Airline_Code":predotherairlines, "Predicted_Average_Fare":predfare})
    
    predmean_df_new.set_index('Airline_Name',inplace=True)
    predsortedmean_df = predmean_df_new.sort_values("Predicted_Average_Fare", ascending =True)

    # print(predsortedmean_df)

    return predsortedmean_df




def findlatlng(airportcode):
  statement = f"select lat, lng from AIRPORT_DETAILS where AIRPORT_CODE ='{airportcode}'"

  result = conn.execute(statement)
  for row in result:
    lat = row["Lat"]
    lng = row["Lng"]
    print(f"Lat : {lat} , lng : {lng}")

  return [lat, lng]






# ## Calculate Mean - tried by calculating the mean - the returned values are very low. So we decided to keep predict approach.
# carriercodes = ["DL","WN","UA","B6","AS","AA","OO","F9","EV", "HA"]
# AverageFare =[]
# otherairlines = []
# def calculateMean(qtr, origin, dest, chosenairline):
#     AverageFare.clear() ## clearing existing values in the list
#     otherairlines.clear()
#     for air in carriercodes: 
#         if air != chosenairline: 
#             query = f"select Market_fare from db1b_details where QUARTER='{qtr}' AND ORIGIN ='{origin}' AND DEST ='{dest}' AND REPORTING_CARRIER ='{air}'"
#             airfare = pd.read_sql(query, conn)
#             numMarket_fare = pd.to_numeric(airfare["MARKET_FARE"])
#             try:
#                 faremean = mean(numMarket_fare)
#                 AverageFare.append(faremean)
#                 otherairlines.append(air)
#             except StatisticsError:    ### mean calculation throw statistics error if the there are no rows 
#                 print(f"This airline {air} is not available for the selected Origin and destination")
            
            
# calculateMean(4, "SFO", "BOS", "OO")
# print(len(otherairlines))
# print(len(AverageFare))

# mean_df_new = pd.DataFrame({"Airline" :otherairlines, "AverageFare" :AverageFare })   
# sortedmean_df = mean_df_new.sort_values("AverageFare", ascending =True)
# sortedmean_df

