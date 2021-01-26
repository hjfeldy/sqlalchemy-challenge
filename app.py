from flask import Flask
from flask.json import jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime

# Import data
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect= True)

#Initiate session
sesh = Session(bind=engine)

#ORM 
Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)

@app.route('/')
def home():
    return open('index.html', 'r').read()

@app.route('/api/v1.0/precipitation')
def precip():
    #Filter & extract data 
    recent = sesh.query(func.max(Measurement.date)).all()
    recent = datetime.datetime.strptime(recent[0][0], '%Y-%m-%d')
    yearAgo = recent - datetime.timedelta(days = 365)
    rainDict = {}
    query = sesh.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= yearAgo)\
            .all()
    print(query)
    #Export to user
    for result in query:
        date = result[0]
        precip = result[1]
        rainDict[date] = precip
    return jsonify(rainDict)

@app.route('/api/v1.0/stations')
def stations():
    stations = []
    query = sesh.query(Station.station).group_by(Station.station).all()
    # Unpack out of annoying tuples
    for station in query:
        stations.append(station[0])
    return jsonify(stations)   

@app.route('/api/v1.0/tobs')
def temp():
    # Step 1: find most active station
    mostActive = sesh.query(Station.station, func.count(Station.station))\
        .group_by((Station.station))\
            .order_by(sqlalchemy.desc(func.count(Station.station)))\
                .limit(1).all()[0][0]

    # Step 2: filter by mostActive and return temp and date data
    recent = sesh.query(func.max(Measurement.date)).all()
    recent = datetime.datetime.strptime(recent[0][0], '%Y-%m-%d')
    yearAgo = recent - datetime.timedelta(days = 365)

    query = sesh.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == mostActive)\
            .filter(Measurement.date >= yearAgo)\
                .all()
    
    return jsonify(query)

@app.route('/api/v1.0/<start>')
def start(start):
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    query = sesh.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).all()
    return jsonify(query)

@app.route('/api/v1.0/<start>/<end>')
def startEnd(start, end):
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    query = sesh.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
            .filter(Measurement.date <= end).all()
    return jsonify(query)


if __name__ == '__main__':
    app.run(debug=True)
