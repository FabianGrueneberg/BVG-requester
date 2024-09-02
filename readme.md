# BVG requester

A docker application to save transit data from the vbb api.

## Table of Contents

* [General Information](#general-information)
* [Technology used](#technology-used)
* [Getting started](#getting-started)
* [Project status](#project-status)
* [Room for improvements](#room-for-improvements)

## General Information

The aim of this project is to get familiar with using Docker and deploying an application onto a server. The "BVG requester" is able to fetch arrival times of busses close to my work and save them into a MongoDB instance. Data can then be pulled via >ip-adress<:8000/arrivals.

"BVG requester" uses three docker container. One for MongoDB, one for an "crawler" sheduling requests to get accurate info on bus delays and one container for a very simplistic webserver which helps to extract the data saved into MongoDB for later evaluation.

There are three access points for the fastapi app:
1. _/_ -> A histogram of all the delays of all saved busses
2. _/arrivals_ -> A json file with all saved bus arrivals times for more in depth analysis
3. _/knownDestimations_ -> A json file with all relevant transit destinations used by the app.

## Technology used

* Docker version 27.2.0, build 3ab4256
* Docker image mongo:4.4
* Docker image python:3.8
* FastAPI

## Getting started

To run the application Docker has to be installed. For ubuntu an installation guide can be found [_here_](https://docs.docker.com/engine/install/ubuntu/).

Once Docker is installed the containers have to be build:

    docker build -t <build-name-crawler> -f Dockerfile-crawler .
    docker build -t <build-name-app> -f Dockerfile-app .

Then a Docker network has to be created with:

    docker network create <network-name>

And finally the containers have to be run with:

    docker run --rm -it -d --net <network-name> --name my-mongodb -p 27017:27017 -v <file-to-save-data>:/data/db mongo:4.4
    docker run --rm -it -d --net <network-name> --name crawler -p 8081:0881 -v <file-to-save-logs>:/opt/crawler/logData <build-name-crawler>
    docker run --rm -it -d --net <network-name> --name app -p 8000:8000 -v <file-to-save-logs>:/opt/app/logData <build-name-app>

## Project status

No longer beeing worked on.

I have leared a lot creating this simple app and moved on the do other interesting projects.

## Room for improvements

* Make the transit station choosable
* Provide some better data analysis on fastapi path "_/_"
* Create a docker compose to simplify deployment


