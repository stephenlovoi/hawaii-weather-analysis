import numpy as np
import datetime as dt
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create Engine and connect to Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Perform Query
    session = Session(engine)
    measurement_query = session.query(*[Measurement.date, Measurement.prcp]).all()
    session.close()

    all_prcp = []
    for date, prcp in measurement_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():

    # Perform Query
    session = Session(engine)
    stat_query = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()
    session.close()

    station_list = []
    for station, freq_count in stat_query:
        stat_dict = {}
        stat_dict['station'] = station
        stat_dict['freq_count'] = freq_count
        station_list.append(stat_dict)
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    #Start Session
    session = Session(engine)

    # Starting from the most recent data point in the database. 
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent = dt.datetime.strptime(recent, '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    year_ago = recent - dt.timedelta(days=365)

    #Perform Query
    temp_query = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date > year_ago).all()

    # Close Session
    session.close()

    temp_list = []
    for station, date, tobs in temp_query:
        temp_dict = {}
        temp_dict['station'] = station
        temp_dict['date'] = date
        temp_dict['tobs'] = tobs
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
