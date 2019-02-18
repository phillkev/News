from flask import Flask, jsonify, json, render_template, url_for, request, redirect
from flask_pymongo import PyMongo

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/comparison')
def comparison():
    return render_template('comparison.html')

@app.route('/data')
def data():
    return render_template('convertcsv.html')

@app.route('/cloudiness')
def cloudiness():
    return render_template('cloudiness.html')

@app.route('/wind_speed')
def wind_speed():
    return render_template('wind_speed.html')

@app.route('/humidity')
def humidity():
    return render_template('humidity.html')

@app.route('/max_temp')
def max_temp():
    return render_template('max_temp.html')


if __name__ == '__main__':
    app.run(debug=True)