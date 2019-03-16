import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

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
myTable = Base.classes.ftp_table


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")


@app.route("/mydata")
def mydata():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query

    # RUNS A QUERY ON THE TABLE TO PULL ALL ROWS AND COLUMNS
    ### CHANGW THIS ##### stmt = db.session.query(myTable).statement

    ## CONVERTS THE OUTPUT OF THE QUERY INTO A PANDAS DATAFRAME
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return JSON VERSION OF THE OUTPUT FROM THE DATAFRAME IN THE /MYDATA ROUTE
    return jsonify(df)

if __name__ == "__main__":
    app.run()
