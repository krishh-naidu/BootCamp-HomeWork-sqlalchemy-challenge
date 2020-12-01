import  sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import numpy as np

from flask import Flask,jsonify

from dateutil.relativedelta import relativedelta
from datetime import datetime, date, time
Base=automap_base()

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app=Flask(__name__)

@app.route('/')
def home():
    return(
        f"welcome to Climate app for Hawaii Perceptation <br/>"
        f"<br/>"
        f"List all available api routes:<br/>"
        f" <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )

@app.route('/api/v1.0/precipitation')
def precipitation():
    
    # create session
    session=Session(engine)

    #Query all precipitation data
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    precipitation_data=[]
    for date,prcp in results:
        precipitation_dict={}
        precipitation_dict['Date']=date
        precipitation_dict['Precipitation']=prcp
        precipitation_data.append(precipitation_dict)
    
    #convert the response to json
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    
    # create a session
    session=Session(engine)

    # qauery all stations
    stations = session.query(Station.station,Station.name).all()
    session.close()
    
    # Return a JSON list of stations from the dataset.
    station_data=[]
    for station,name in stations:
        station_dict={}
        station_dict['Station ID']=station
        station_dict['Station Name']=name
        station_data.append(station_dict)
    
    #convert the response to json
    return jsonify(station_data)

@app.route('/api/v1.0/tobs')
def tobs():

    # create a session
    session=Session(engine)

    # qauery latest_date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date=datetime.strptime(latest_date[0],'%Y-%m-%d').date()

    date_1year_ago = latest_date - relativedelta(months=12)

    # Query for temperature in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= date_1year_ago).all()

    session.close()
    
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperature_data.append(temperature_dict)  

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create session from Python to the DB
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    temps_stats_results = list(np.ravel(temperature_stats))
    
    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]
    
    temp_stats_data= []
    temp_stats_dict = [{"Start Date": start},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_stats_data.append(temp_stats_dict)
    
    return jsonify(temp_stats_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_stats_results = list(np.ravel(temperature_stats))
    
    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]
    
    temp_stats_data = []
    temp_stats_dict = [{"Start Date": start_date},
                       {"End Date": end_date},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_stats_data.append(temp_stats_dict)
    
    return jsonify(temp_stats_data)

if __name__  == "__main__":
    app.run(debug=True)