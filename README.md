# NL Stats
This project is a web application and ETL pipeline for the [NL Stats website](https://nlstats.com).  The
website collects, aggregates and displays various stats for NorthernLion's YouTube
channel.

## webapp
This folder contains the code for the web application.  It uses the
[Python Dash](https://dash.plotly.com/introduction) framework.

## etl
This folder contains the code for the ETL pipeline application.  It connects to YouTube
and extracts the channel data, then transforms it into something usable for the website
and loads it into a Postgres database.

## Questions
For questions contact nyteowldev (at) gmail.
