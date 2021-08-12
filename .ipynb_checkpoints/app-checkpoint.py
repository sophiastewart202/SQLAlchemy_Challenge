# Import Necessities
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query
from sqlalchemy import create_engine, func, inspect, join
from sqlalchemy.sql import select

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create an app
app = Flask(__name__)


# Define static routes
# Home page
@app.route("/")
def home():
    print('Climate App home page requested')
    
    # List all routes that are available.
    return(
    "Welcome to Hawaii's Climate App!<br/>
    "--------------------------------<br/>"
    "Available Routes:<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/<start><br/>"
    "/api/v1.0/<start>/<end><br/>"
    "---------------------------------------------------------------------<br/>"
    "Note: Replace <start> and <end> with query dates in YYYY-MM-DD format.<br/>"
    )


# Precipitation page
@app.route('/api/v1.0/precipitation')
def precipitation():
    print('Precipitation page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Convert the query results to a dictionary using date as the key and prcp as the value

    # Return the JSON representation of the dictionary
    return jsonify(prcp)

# Stations page
@app.route('/api/v1.0/stations')
def stations():
    print('Stations page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve all station data
    results = session.query(station.id, station.station, station.name).all()
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    stn_data = []
    for stn in results:
        stn_dict = {}
        stn_dict['id'] = stn[0]
        stn_dict['station'] = stn[1]
        stn_dict['name'] = stn[2]
    
        stn_data.append(stn_dict)
    
    # Return a JSON list of stations from the dataset.
    return jsonify(stn_data)
    
    
# Temperature Observations page
@app.route('/api/v1.0/tobs')
def tobs():
    print('Tobs page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.

    # Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route(f'/api/v1.0/<start> {and} /api/v1.0/<start>/<end>')