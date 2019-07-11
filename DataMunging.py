from config import API_key
import requests
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.orm import join
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, Float

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from statistics import mean , StatisticsError

# #################################################################
# # DATA RETRIEVAL AND MUNGING FOR AIRPORT DETAILS
# #################################################################

AirportCodes = ["ATL", "BOS", "DAL", "DEN", "FLL", "JFK", "LAS", "LAX", "PDX", "SFO"]

AirportAddress =[]
Lat = []
Lng = []
AirportName = []
counter = 0


##### Gathering the Airport address , lat and Lng values of the airports #########
for airport_code in AirportCodes: 

    URL = f"https://maps.googleapis.com/maps/api/geocode/json?address={airport_code}&key={API_key}"

    results = requests.get(URL).json()

    formatted_address = results["results"][0]["formatted_address"]
    lat = results["results"][0]["geometry"]["location"]["lat"]
    lng = results["results"][0]["geometry"]["location"]["lng"]

    short_name = results["results"][0]["address_components"][0]["short_name"]
    airportname = short_name.split(" Airport")[0]  ## removing the Airport from the name
    
     
    # Inserting the gathered values to their respective Lists.
    AirportAddress.append(formatted_address)
    Lat.append(lat)
    Lng.append(lng)
    AirportName.append(airportname)
#     # print (f"{counter} : Airport Name : {airportname} --- Airport Code:{airport_code}")
    
### Insert the list to a DataFrame before inserting to SQL

AirportDetailsDF = pd.DataFrame({"AIRPORT_NAME" : AirportName,
                                 "AIRPORT_CODE" : AirportCodes,
                                "AIRPORT_ADDRESS" : AirportAddress,
                                "Lat" :Lat, 
                                "Lng" :Lng
                                })


######## Finding the Airline Codes only for the selected Airlines list below  ###############################

Airlines = ["Hawaiian Airlines Inc.",
"Delta Air Lines Inc.",
"United Air Lines Inc.",
"American Airlines Inc.",
"Frontier Airlines Inc.",
"Southwest Airlines Co.",
"JetBlue Airways",
"ExpressJet Airlines LLC",
"SkyWest Airlines Inc.",
"Alaska Airlines Inc."]

EntireCarrierDF = pd.read_csv("./Resources/L_CARRIERS.csv")
EntireCarrierDF.set_index("Code")

CarrierCode = []

for airline in Airlines: 
    code = list(EntireCarrierDF.loc[EntireCarrierDF["Description"]== airline, "Code"])
    CarrierCode.append(code[0])

CarrierCodeDF = pd.DataFrame({"Code":CarrierCode})

FinalCarrierCodeDF = pd.merge(EntireCarrierDF,CarrierCodeDF, how="inner", on="Code" )

FinalCarrierCodeDF.rename(columns={"Description":"AIRLINES_NAME", "Code":"AIRLINES_CODE"}, inplace=True)

#################################################################
# ORIGIN AND DESTINATION SURVEY DATA
#Airline Origin and Destination Survey (DB1B)
#################################################################

q12018 = pd.read_csv("./Resources/789605885_T_DB1B_MARKET_Q1.csv")
q22018 = pd.read_csv("./Resources/789605885_T_DB1B_MARKET_Q2.csv")
q32018 = pd.read_csv("./Resources/789605885_T_DB1B_MARKET_Q3.csv")
q42018 = pd.read_csv("./Resources/789605885_T_DB1B_MARKET_Q4.csv")

DB1Bframes = [q12018,q22018, q32018,q42018]
EntireDB1B_dataDF = pd.concat(DB1Bframes)   ####  Number of rows 27,234,768‬  (2GB of data)

DB1B_dataDF = pd.merge(EntireDB1B_dataDF, FinalCarrierCodeDF, how ="inner", left_on="REPORTING_CARRIER", right_on="AIRLINES_CODE")

# drop the "Unnamed column - which is added by default"
DB1B_dataDF_new = DB1B_dataDF.dropna(how='all', axis='columns')

# Drop the columns that are not needed

DB1B_dataDF = DB1B_dataDF_new.drop(["ORIGIN_COUNTRY", "ORIGIN_STATE_ABR", "DEST_STATE_ABR", "AIRLINES_CODE"], axis=1)

# Filter the "ORIGIN" column with the "AIRPORT_CODE" of ten selected Airports - DB1B_dataDF_Origin - Intermediate dataset

DB1B_dataDF_Origin = pd.merge(DB1B_dataDF, AirportDetailsDF, how ="inner", left_on=["ORIGIN"], right_on=["AIRPORT_CODE"])

# Dropping the merged columns to merge again for the "DEST" column
DB1B_dataDF_origin_clean = DB1B_dataDF_Origin.drop(['AIRPORT_NAME', 'AIRPORT_CODE',
                                                    'AIRPORT_ADDRESS', 'Lat', 'Lng'], axis=1)

# Merging again in "DEST" column and "AIRPORT_CODE" 
DB1B_dataDF_origin_dest_clean = pd.merge(DB1B_dataDF_origin_clean, AirportDetailsDF, how ="inner", left_on=["DEST"], right_on=["AIRPORT_CODE"])                                                    

DB1B_dataDF_origin_dest_clean["ORIGIN"].value_counts()   #  show the ten chosen airports
DB1B_dataDF_origin_dest_clean["DEST"].value_counts()  #  show the ten chosen airports
DB1B_dataDF_origin_dest_clean["REPORTING_CARRIER"].value_counts() # show the ten chosen Airlines

# Dropping the merged columns again - these columns will go into "airport_details" table

DB1B_dataDF_origin_dest_clean_new = DB1B_dataDF_origin_dest_clean.drop(['AIRPORT_NAME', 'AIRPORT_CODE',
       'AIRPORT_ADDRESS', 'Lat', 'Lng'], axis=1)

# Renaming the column
DB1B_dataDF_origin_dest_clean_new.rename(columns={"Description":"AIRLINES_NAME"}, inplace=True)



#### removing the rows where the MARKET_FARE has < 200 value and market_distance <200 miles. 

cleanDB1B_dataDF  = DB1B_dataDF_origin_dest_clean_new[DB1B_dataDF_origin_dest_clean_new.MARKET_FARE > 200] 

cleanDB1B_dataDF_clean  = cleanDB1B_dataDF[cleanDB1B_dataDF.MARKET_DISTANCE > 200]

##### Drop more columns that are not needed to reduce DB space.
cleanDB1B_dataDF_new =  cleanDB1B_dataDF_clean.drop(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID", "DEST_STATE_NM", "ORIGIN_STATE_NM" ,"AIRLINES_NAME"], axis=1) 


# # # #######################################
# # # Inserting to the SQL Lite database 
# ##########################################

engine = create_engine("sqlite:///db/flight1.sqlite")
Base = declarative_base()

class Airport_Details(Base):
    __tablename__ = 'airport_details'
    ID = Column(Integer, primary_key=True)
    AIRPORT_NAME = Column(String(255))
    AIRPORT_CODE = Column(String(255))
    AIRPORT_ADDRESS = Column(String(255))
    Lat = Column(String(255))
    Lng = Column(String(255))

class Airlines_details(Base):
    __tablename__ = 'airlines_details'
    ID = Column(Integer, primary_key=True)
    AIRLINES_NAME = Column(String(255))
    AIRLINES_CODE = Column(String(255))
    


class DB1B_Details(Base):
    __tablename__ = 'db1b_details'
    ID = Column(Integer, primary_key=True)
    QUARTER = Column(String(255))
    ORIGIN = Column(String(255))
    DEST = Column(String(255))
    REPORTING_CARRIER = Column(String(255))
    PASSENGERS = Column(String(255))
    MARKET_FARE = Column(String(255))
    MARKET_DISTANCE = Column(String(255))
    MARKET_MILES_FLOWN = Column(String(255))
    NONSTOP_MILES = Column(String(255))
    # AIRLINES_NAME = Column(String(255))

Base.metadata.create_all(engine)
session = Session(bind=engine)

try:
    AirportDetailsDF.to_sql('airport_details', con=engine, if_exists="append", index= False)
    cleanDB1B_dataDF_new.to_sql('db1b_details', con=engine, if_exists="append", index= False, chunksize=10000)
    FinalCarrierCodeDF.to_sql('airlines_details', con=engine, if_exists="append", index= False)
    
    print("Tables added successfully")
except Exception as e:
    print("Problems adding tables" + str(e))

