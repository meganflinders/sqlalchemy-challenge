# Import the dependencies.
import numpy as np
import re
import datetime as dt
import sqlalchemy
import flask 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists
from flask import Flask, jsonify
import warnings
warnings.filterwarnings('ignore')


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (f'''
    Welcome!
    Available Routes:<br/>
    /api/v1.0/precipitation <br/>
    /api/v1.0/stations <br/>
    /api/v1.0/tobs <br/>
    /api/v1.0/<start> <br/>
    /api/v1.0/<start>/<end>
    ''')
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    prcp_date_tobs = []
    for row in year_precipitation:
        results  = {}
        results["date"] = year_precipitation[0]
        results["prcp"] = year_precipitation[1]
        prcp_date_tobs.append(results)
    return jsonify(prcp_date_tobs)

#Return JSON list of stations from dataset

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.name).all()
    station_list = list(np.ravel(stations))
    return jsonify(station_list)

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return JSON list of temperature observations for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    temperature = session.query(measurement.date, measurement.tobs).filter(measurement.date > year_ago).filter(measurement.station=='USC00519281').order_by(measurement.date).all()
    temp_totals = []
    for row in temperature:
        results = {}
        results["date"]  = temperature[0]
        results["prcp"] = temperature[1]
        temp_totals.append(results)
    return jsonify(temp_totals)

@app.route("/api/v1.0/<start>")
def start_only(start):
    start_temp_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    return jsonify(start_temp_results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    start_end_temp_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    return jsonify(start_end_temp_results)

if __name__ == "__main__":
    app.run(debug=True)
