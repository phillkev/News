from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask import Markup
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_info")

# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    result_data = list(mongo.db.mars.find())
    article = result_data[0]['articles']
    main_photo = result_data[0]['main photo']
    weather = result_data[0]['weather']
    facts = Markup(result_data[0]['facts'])
    hires = result_data[0]['hi-res']
    return render_template('index.html', article=article, main_photo=main_photo, weather=weather, facts=facts, hires=hires)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True       
    mongo.db.mars.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)