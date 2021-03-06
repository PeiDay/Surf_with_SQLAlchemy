# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask and jsonify
from flask import Flask, jsonify

# Engines and Database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Set up Flask
app = Flask(__name__)


# Welcome homepage
@app.route("/")

def Welcome():
    """All the available routes:"""
    return(
        f"- Welcome to the Weather App Home Page -<br/>"
        f"<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Enter a start date to retrieve the weather info : /api/v1.0/yyyy-mm-dd<br>"
        f"Enter a start and end date to retrieve the weather info : /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br>"
        )


# precipitation route
@app.route("/api/v1.0/precipitation") 

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.

def precipitation():
    select = [measurement.date, measurement.prcp]
    result_prcp = session.query(*select).all()
    session.close()

    precipitation = []
    for date, prcp in result_prcp:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp

        # append results to a dict
        precipitation.append(prcp_dict)
        
    # return json list of dict    
    return jsonify(precipitation)


# Stations route
@app.route("/api/v1.0/stations")

# Return a JSON list of stations from the dataset.

def stations():
    stations = session.query(station.name, station.station).all()
    session.close()

    # convert results to a dict
    stations_dict = dict(stations)

    # return json list of dict
    return jsonify(stations_dict)


# Tobs routes
@app.route("/api/v1.0/tobs")

# Query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.

def tobs():

    prioryear = dt.date(2017,8,23) - dt.timedelta(days = 365)
    result_tobs = session.query(measurement.tobs, measurement.date).\
        filter(measurement.date >= prioryear).all()

    session.close()

    tobs_ls = []
    for tobs, date in result_tobs:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs

        # append results to a dict
        tobs_ls.append(tobs_dict)

    # return json list of dict
    return jsonify(tobs_ls)
    

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for 
# all dates greater than and equal to the start date. @app.route("/api/v1.0/<start>")

# When given the start and the end date, calculate the `TMIN`, `TAVG`, 
# and `TMAX` for dates between the start and end date inclusive. @app.route("/api/v1.0/<start>/<end>")


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start = None, end = None):


    """Return a list of min, avg and max tobs for the start date"""

    select = [func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)]

    if not end:
        result = session.query(*select).filter(measurement.date >= start).all()
    else:
        result = session.query(*select).filter(measurement.date >= start)\
        .filter(measurement.date <= end).all()
        
    session.close()

    # Create a dictionary from the row data and append to a list of start_tobs
    # dates_tobs = []
    # for min, max, avg in result:
    #     dates_tobs_dict = {}
    #     dates_tobs_dict["min_temp"] = min
    #     dates_tobs_dict["max_temp"] = max
    #     dates_tobs_dict["avg_temp"] = avg
    #     dates_tobs.append(dates_tobs_dict) 

    dates_tobs = list(np.ravel(result))

    return jsonify(dates_tobs)

if __name__ == '__main__':
    app.run(debug=True)