# Technology Debt Score and ROI Calculator

A web app that analyzes a portfolio of legacy applications, scores their "technology debt", and estimates the savings and ROI of retiring or migrating them.

> This is a simplified demo model built for learning. It is not any company's proprietary method.

![App screenshot](screenshot.png)

## Problem

Companies often keep old applications running that cost a lot and have few users. This tool helps decide which ones to retire or migrate first.

## Features

- Upload a CSV of applications (or use the built-in sample data)
- Data cleaning: removes duplicates, fixes currency and Yes/No formats, handles missing values
- Rejects invalid rows and reports the reason
- Debt score (0-100) with High / Medium / Low priority
- Net savings and ROI over an adjustable number of years
- Charts, ranked table, and downloadable CSV report

## How the debt score works

| Factor | Max points | Logic |
|---|---|---|
| Age | 30 | older applications score higher (capped at 15 years) |
| Cost per user | 30 | expensive per active user scores higher |
| Low usage | 20 | fewer than 200 users scores higher |
| No vendor support | 20 | unsupported applications get the full 20 |

Priority: 70+ High, 40-69 Medium, below 40 Low.

Net savings = yearly cost x years - migration cost

ROI % = net savings / migration cost x 100

## Tech stack

Python, Pandas, Streamlit

## Run locally

    pip install pandas streamlit
    python -m streamlit run app.py

## Project structure

- app.py: Streamlit user interface
- scoring.py: data cleaning and scoring logic
- sample_apps.csv: sample messy dataset

## Future improvements

- Store results in a SQL database
- Add archival flagging for old records
- Make score weights adjustable in the UI