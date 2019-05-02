# Import dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# Create engine
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect databases into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
#Base.classes.keys()

# Save a reference to tables
Station = Base.classes.hawaii_station
Measurement = Base.classes.hawaii_measurement

# Create session link
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"Avalable Routes:<br/>"
         
         f"/api/v1.0/precipitation<br/>"
         f"- JSON representation of dictionary<br/>"
         
         f"/api/v1.0/stations<br/>"
         f"- JSON list of weather stations<br/>"

         f"/api/v1.0/tobs<br/>"
         f"- JSON list of tobs from previous year<br/>"

         f"/api/v1.0/<start><br/>"
         f"- JSON list of min, avg, and max temperature for a given start date<br/>"
        
         f"/api/v1.0/<start>/<end><br/>"
         f"- JSON list of min, avg, and max temperature for a given start/end range<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """JSON representation of dictionary """
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert query into dictionary
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)
    
@app.route("/api/v1.0/stations")
def stations():
    """JSON list of weather stations """
    # Query all stations
    results = session.query(Station.station).all()
    stations_list = list(np.ravel(results))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """JSON list of tobs from previous year """
    # Query for all temperature observations from previous year
    results = session.query(Measurement.date, Measurement.tobs).\
        group_by(Measurement.date).\
        filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.date >= '2016-08-23').all()

    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """JSON list of min, avg, max for specific dates"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results= session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps2 = list(np.ravel(results))
    return jsonify(temps2)

if __name__ == '__main__':
    app.run()