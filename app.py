import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.automap import automap_base


import requests
from bs4 import BeautifulSoup as bs

import pymongo
#import matplotlib.pyplot as plt

import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, plot, iplot


app = Flask(__name__)


#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://ysodzkuphrfgoj:84ff3e242c8003e2b705786424d7281e85ba2a9496e9065bb9c12021cc982e75@ec2-50-19-109-120.compute-1.amazonaws.com:5432/d6ml7dnjt0ajnc"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
#myTable = Base.classes.numbers_table

# Use Pandas to perform the sql query, converts it into a pandas df
df = pd.read_sql_query("select * from numbers_table", db.session.bind)

# read new_df csv file
url = 'https://www.the-numbers.com/weekly-box-office-chart'

#make a call to the internet page
response = requests.get(url)

#parse the text version of the response using an html parser 
soup = bs(response.text, 'html.parser')

#finds the table in the HTML page
all_table_data = soup.find_all('table')

#finds and isolates only the <tr> tags and subtags within the above table
rows = soup.find_all('tr')

#start an empty master list of rows
data = []

#loop through each row
for row in rows:
    #each cell is a column within that row, so you use <td> to find each cell
    cols = row.find_all('td')
    #add the cells to a preliminary list using list comprehensions (this is is for a single row)
    cols = [element.text.strip() for element in cols]
    #add that preliminary list to the master list of rows
    data.append([element for element in cols])

df = pd.DataFrame(data)

# drop first two rows
df.drop([0,1], inplace=True)

df.columns = ["Rank", "Last Rank", "Movie", "Distributor", "Gross", "Change", "Theatres", "Per Theatre", "Total Gross", "Week"]

# Make a copy of dataframe
new_df = df.copy()

# remove all dollar signs
new_df['Gross'] = [x.strip('$') for x in df['Gross']]
new_df['Per Theatre'] = [x.strip('$') for x in df['Per Theatre']]
new_df['Total Gross'] = [x.strip('$') for x in df['Total Gross']]

# remove all commas and create new clean dataframe
new_df['Gross'] = new_df['Gross'].str.replace(',', '')
new_df['Theatres'] = new_df['Theatres'].str.replace(',', '')
new_df['Total Gross'] = new_df['Total Gross'].str.replace(',', '')

# create new dataframe isolating movie, distributor, total gross revenue
movie_gross_df = new_df[["Movie", "Distributor", "Total Gross"]]

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/numbers_data")
def numbers_data():
    """Return a list of sample names."""
    movie_gross_df["Total Gross"] = movie_gross_df["Total Gross"].astype(int)
    dist_gross_count = movie_gross_df.groupby("Distributor").count()["Total Gross"]
    dist_gross_sum = movie_gross_df.groupby("Distributor").sum()["Total Gross"]

    # combine the data into a single dataset using pandas merge
    merged_df = pd.DataFrame(
        data={"TotalGrossAllMovies": dist_gross_sum,
            "NumMovies": dist_gross_count,
        }
    )
    merged_df.reset_index(inplace=True)

    merged_df = merged_df.sort_values("TotalGrossAllMovies", ascending=False).head()

    # convert to dictionary and jsonify (returns json version of the df output)
    return jsonify(merged_df.to_dict(orient="list"))

    twentieth_c_fox = new_df[new_df["Distributor"] == "20th Century Fox"]
    # convert to dictionary and jsonify (returns json version of the df output)
    return jsonify(twentieth_c_fox.to_dict(orient="list"))

    # isolated dataset for twentieth century fox releases
    # films = ["Bohemian Rhapsody", "Widows", "Once Upon a Deadpool", "The Hate U Give"]
    # total_gross = [195296306, 42162140, 324574517, 29705000] 

if __name__ == "__main__":
    app.run()
