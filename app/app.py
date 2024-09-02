from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import logging
import logging.config
import configparser
import datetime
import json

# Load configs
config = configparser.ConfigParser()
config.read("setup.ini")

# setup DB
mongoClient = MongoClient(
    str(config["CONTAINER"]["DB"]), port=int(config["CONTAINER"]["DBPort"])
)
dbPath = mongoClient.client.BVG

# create API app
app = FastAPI()
app.client = mongoClient
app.db = dbPath
app.startTime = datetime.datetime.now()

# setup logging
with open(str(config["LOGGING"]["relativeConfigPath"]), "r") as loggingConfig:
    logging.config.dictConfig(json.load(loggingConfig))
logging.info(f"App started.")


def generateHTML(histData, serverStartTime):
    fig = go.Figure(
        data=[
            go.Histogram(
                x=histData,
                xbins=dict(
                    size=1,
                ),
                opacity=0.75,
            )
        ]
    )
    fig.update_layout(
        title="",
        xaxis_title="Delay",
        yaxis_title="Count",
        template="plotly_white",
        autosize=True,
        height=None,
    )

    plot_html = pio.to_html(fig, full_html=False)
    mean = np.mean(histData)
    std_dev = np.std(histData)
    three_sigma = 3 * std_dev
    serverStartTimeString = serverStartTime.strftime("%Y-%m-%d %H:%M")

    with open(config["FRONTEND"]["htmlBody"], "r") as f:
        html_content = f.read().format(
            plot_html=plot_html,
            mean=mean,
            std_dev=std_dev,
            three_sigma=three_sigma,
            numberOfDataPoints=histData.shape[0],
            startTime=serverStartTimeString,
        )

    return html_content


@app.get("/")
async def root():
    """

    Entrypoint "/" to server. Displays the measured statistics.

    Returns
    -------
    dict
        A html-file.
    """
    data = app.db.bus_arrivals.find()
    histData = np.array([d["delay"] for d in list(data)])
    histData = histData[np.where(histData != None)]
    histData = histData / 60
    html = generateHTML(histData, app.startTime)
    return HTMLResponse(content=html)


@app.get("/arrivals")
async def getAllStations():
    """
    Entrypoint "/arrivals" to get access to all known arrivals in the DB

    Returns
    -------
    dict
        All arrivals in a long list inside the dict.
    """
    return {"bus_arrivals": list(app.db.bus_arrivals.find())}


@app.get("/knownDestinations")
async def getKnownDestinations():
    """
    Entrypoint "/knownDiestinations" to get all known destinations in the DB

    Returns
    -------
    dict
        All known stations in a list inside the dict.
    """
    return {"bus_arrivals": list(app.db.stations.find())}
