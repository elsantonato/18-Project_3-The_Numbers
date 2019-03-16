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


@app.route("/names")
def names():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(myTable).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return a list of the column names (sample names)
    return jsonify(list(df.columns)[2:])


@app.route("/metadata/<sample>")
def myTable(sample):
    """Return the MetaData for a given sample."""
    sel = [
        myTable.YEAR,
        myTable.CLIENT,
        myTable.PROJECT,
        myTable.ROLE,
        myTable.TYPE,
        myTable.INDUSTRY,
        myTable.EVENT,
    ]

    results = db.session.query(*sel).all()

    # Create a dictionary entry for each row of metadata information
    myTable = {}
    for result in results:
        myTable["YEAR"] = result[0]
        myTable["CLIENT"] = result[1]
        myTable["PROJECT"] = result[2]
        myTable["ROLE"] = result[3]
        myTable["TYPE"] = result[4]
        myTable["INDUSTRY"] = result[5]
        myTable["EVENT"] = result[6]

    print(myTable)
    return jsonify(myTable)


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]
    # Format the data to send as json
    data = {
        "otu_ids": myTable.otu_id.values.tolist(),
        "sample_values": myTable[sample].values.tolist(),
        "otu_labels": myTable.otu_label.tolist(),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()
