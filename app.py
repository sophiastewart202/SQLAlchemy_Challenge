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

# Set up
engine = create_engine("sqlite:///Resources\hawaii.sqlite", echo=False)

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
    "Welcome to Hawaii's Climate App!<br/>"
    "-------------------------------------------<br/>"
    "Available Routes:<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/&lt;start&gt;<br/>"
    "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    "---------------------------------------------------------------------------------------------<br/>"
    "Note: Replace &lt;start&gt; and &lt;end&gt; with query dates in YYYY-MM-DD format.<br/>"
    )




# Precipitation page
@app.route('/api/v1.0/precipitation')
def precipitation():
    print('Precipitation page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate last year of data
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_yr_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
    

    # Query to retreive all precipitation data
    results = session.query(measurement.date, measurement.prcp)\
    .filter(measurement.date>=one_yr_ago).all()
    
    session.close()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_data = []
    for item in results:
        prcp_dict = {}
        prcp_dict['date'] = item[0]
        prcp_dict['prcp'] = item[1]
    
        prcp_data.append(prcp_dict)
    
    # Return the JSON representation of the dictionary
    return jsonify(prcp_data)




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

    # Calculate last year of data
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_yr_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the last year of data.
    most_active_stn = session.query(measurement.station, func.count(measurement.station))\
    .group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()[0][0]
    
    results = session.query(measurement.tobs)\
    .filter(measurement.station==most_active_stn).filter(measurement.date>=one_yr_ago).all()
    
    session.close()
    
    # Convert query results to a list
    tobs_data = list(np.ravel(results))
    
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_data)




@app.route(f'/api/v1.0/<start>')
def summary_from(start):
    print('Tobs summary page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the min temp, the avg temp, and the max temp for a given start range
    def calc_temps(start_date):
        """TMIN, TAVG, and TMAX for a list of dates.
    
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        
        Returns:
            TMIN, TAVE, and TMAX
        """
    
        return session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
            func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).all()
    
    try:
        # convert the provided start & end dates into a format the calc_temps function can read
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        
        # Enter into the query
        results = calc_temps(start_date)
        session.close()
        
        # Convert query results to a list
        temp_summary = []
        for item in results:
            summary_dict = {}
            summary_dict['t-min'] = item[0]
            summary_dict['t-avg'] = item[1]
            summary_dict['t-max'] = item[2]
        
            temp_summary.append(summary_dict)
            
        # Return a JSON list of the min, the avg, and the max temp for a given start-end range.
        return jsonify(temp_summary)
    
    except:
        return "An error occurred. Please enter query dates in YYYY-MM-DD format."
    
    
    

@app.route('/api/v1.0/<start>/<end>')
def summary_btwn(start, end):
    print('Tobs summary page requested')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the min temp, the avg temp, and the max temp for a given start-end range
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
    
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        
        Returns:
            TMIN, TAVE, and TMAX
        """
    
        return session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
            func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    
    try:
        # convert the provided start & end dates into a format the calc_temps function can read
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
        
        # Enter into the query
        results = calc_temps(start_date, end_date)
        session.close()
        
        # Convert query results to a list
        temp_summary = []
        for item in results:
            summary_dict = {}
            summary_dict['t-min'] = item[0]
            summary_dict['t-avg'] = item[1]
            summary_dict['t-max'] = item[2]
        
            temp_summary.append(summary_dict)
            
        # Return a JSON list of the min, the avg, and the max temp for a given start-end range.
        return jsonify(temp_summary)
    
    except:
        return "An error occurred. Please enter query dates in YYYY-MM-DD format."
    
    
    

if __name__ == "__main__":
    app.run(debug=True)