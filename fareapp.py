
from flask import Blueprint, render_template, abort, jsonify,render_template, request, redirect
from jinja2 import TemplateNotFound
from predictfare import predictMarketFare, predictallairfare, findlatlng
import os
import pandas as pd
import numpy as np

fareapp = Blueprint('fareapp', __name__, template_folder='templates')



@fareapp.route("/predictfare/<qtr>/<origin>/<dest>/<airline>") 
def predictfare(qtr, origin, dest, airline):
   
   mean_preds =  predictMarketFare(qtr, origin, dest, airline)
   return jsonify(mean_preds)


@fareapp.route("/predictallfare/<qtr>/<origin>/<dest>/<airline>") 
def predictall(qtr, origin, dest, airline):
   
   allairpreds = predictallairfare(qtr, origin, dest, airline)
   
   jsonallairpreds=allairpreds.to_json()

   return jsonallairpreds

@fareapp.route("/getlatlng/<airportcode>") 
def getlatlng(airportcode):
   
   result=findlatlng(airportcode)

   return jsonify(result)