from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
import httpx
import threading
import logging
import datetime
from pymongo import MongoClient
import configparser
import pause
import json


# load configs
config = configparser.ConfigParser()
config.read("setup.ini")

# setup db
mongoClient = MongoClient(
    str(config["CONTAINER"]["DB"]), port=int(config["CONTAINER"]["DBPort"])
)
dbPath = mongoClient.client.BVG

# setup logging
with open(str(config["LOGGING"]["relativeConfigPath"]), "r") as loggingConfig:
    logging.config.dictConfig(json.load(loggingConfig))
logging.info(f"App started.")

# create API app
app = FastAPI()
app.fetchNewArrivalsInterval = int(config["CRAWLER"]["FetchNewArrivalsInterval"])  # min
app.expectedArrivals = []
app.client = mongoClient
app.db = dbPath
app.startTime = datetime.datetime.now()


def createThreadsForSingleArrivalRequests(newExpectedArrivals):

    # filter for only the arrivals which have no threads allready created
    currentlyExpectedArrivalsuID = [
        createUniqueIdentifierArrival(cEA) for cEA in app.expectedArrivals
    ]
    expectedArrivalsWithoutThread = []
    for nEA in newExpectedArrivals:
        if createUniqueIdentifierArrival(nEA) not in currentlyExpectedArrivalsuID:
            expectedArrivalsWithoutThread.append(nEA)

    # make new arrivals to old arrivals
    app.expectedArrivals = sorted(
        expectedArrivalsWithoutThread, key=lambda k: k["plannedWhen"]
    )

    # infodump for debugging
    logging.debug(
        f"Theads created for: {' | '.join([createUniqueIdentifierArrival(cEA) for cEA in app.expectedArrivals])}"
    )

    for i, eA in enumerate(app.expectedArrivals):
        time = datetime.datetime.fromisoformat(eA["plannedWhen"])
        threading.Thread(
            target=getSingleArrival, args=(app.db, time, eA["direction"]), daemon=True
        ).start()


def fetchNewExpectedArrivals(duration):
    # fetch all arrivals in the next duration min from stop 900001151.
    ret = httpx.get(
        f"https://v6.vbb.transport.rest/stops/900001151/departures?duration={duration}"
    )

    return ret.json()["departures"]


def getStationID(db, query):
    # try to find station in DB
    resultsFromDB = db.find_one({"name": query})
    if resultsFromDB is not None:
        return resultsFromDB["location"]["id"]
    resultsFromDB = db.find_one({"queryName": query})
    if resultsFromDB is not None:
        return resultsFromDB["location"]["id"]

    # get station from API
    ret = httpx.get(f"https://v6.vbb.transport.rest/locations?query={query}&results=1")
    newStation = ret.json()[0]
    newStation["queryName"] = query
    newStation["_id"] = newStation["location"]["id"]
    db.insert_one(newStation)

    return newStation["location"]["id"]


def getSingleArrival(db, datetime, direction):

    # fetch bus data at the time the bus should arrive
    pause.until(datetime)
    time = f"{datetime.hour}:{datetime.minute}"

    # fetch arrival data from APi
    ret = httpx.get(
        f"https://v6.vbb.transport.rest/stops/{getStationID(db.stations, 'Reuchlinstr.')}/departures?when={time}&direction={getStationID(db.stations, direction)}&results=1"
    )
    arrival = ret.json()["departures"][0]

    # add unique identifier
    arrival["_id"] = createUniqueIdentifierArrival(arrival)

    # add arrival to database
    db.bus_arrivals.insert_one(arrival)


def createUniqueIdentifierArrival(singleBus):
    return f"{singleBus['direction']}{singleBus['plannedWhen']}"


@app.on_event("startup")
@repeat_every(seconds=60 * app.fetchNewArrivalsInterval)
def loop() -> None:

    newExpectedArrivals = fetchNewExpectedArrivals(app.fetchNewArrivalsInterval)

    createThreadsForSingleArrivalRequests(newExpectedArrivals)
