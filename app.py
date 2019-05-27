
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, inspect, func

import numpy as np
import pandas as pd

import datetime as dt

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker 

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#calculate max date with max function (func.max)
max_date=session.query(func.max(Measurement.date)).all()[0][0]

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    # Query all passengers
    max_date=session.query(func.max(Measurement.date)).all()[0][0]
    prev_year = dt.datetime.strptime(max_date,"%Y-%m-%d") - dt.timedelta(days=365)
    sel = [Measurement.date,Measurement.prcp]
    year_data=session.query(*sel).\
    filter(Measurement.date >= prev_year).all()


    # Convert list of tuples into normal list
    all_prcp =[]
    for day in year_data:
        prcp_dict={}
        prcp_dict["date"]=day[0]
        prcp_dict["prcp"]=day[1]
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Measurement.station).\
    group_by(Measurement.station).all()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    prev_year = dt.datetime.strptime(max_date,"%Y-%m-%d") - dt.timedelta(days=365)
    tobs_data=session.query(Measurement.tobs).\
    filter(Measurement.date >= prev_year).all()

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def starter(start):
    session=Session(engine)
    max_date=session.query(func.max(Measurement.date)).all()[0][0]
    def calc_temps(start_date):
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= max_date).all()
    
    return jsonify(calc_temps(start))

@app.route("/api/v1.0/<start>/<end>")
def ender(start,end):
    session=Session(engine)
    def calc_temps(start_date,end_date):
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    return jsonify(calc_temps(start,end))

if __name__ == '__main__':
    app.run(debug=True)
