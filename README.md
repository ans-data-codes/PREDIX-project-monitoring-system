# PREDIX-project-monitoring-system

### AI-Powered Predictive Infrastructure Monitoring & Early Warning System

> **PAIMANA tells us what is happening. PREDIX tells us what is likely to happen next.**

## Overview

PREDIX is an AI-powered decision-support platform designed to help monitor large Central Sector infrastructure projects and identify potential cost overruns, schedule delays, and implementation risks before they materialize.

## Presentation dashboard

The project includes a polished, interactive Streamlit demonstration dashboard with four views: portfolio monitoring, project detail, portfolio analytics, and an early-warning center. It is deliberately transparent about its data status: **only the 1,775 ongoing-project total is attributed to the July 2026 PAIMANA report; all risk scores, project profiles, distributions, and analytic values are illustrative prototype content.**

Run it locally:

```bash
python -m pip install -r requirements.txt
streamlit run src/app/app.py
```

The system analyzes project information such as cost, expenditure, physical progress, timelines, sector, state and implementing agency to generate predictive risk assessments and explainable early warnings.

PREDIX is developed as a prototype for **Smart India Hackathon 2026 — SIH26103**.

## Problem

Existing infrastructure project monitoring provides valuable information about the current status of projects.

However, monitoring can be extended from:

**Descriptive Monitoring → Predictive Monitoring → Early Warning**

Instead of only asking:

> "What is happening to this project?"

PREDIX aims to answer:

> "What is likely to happen next, and why?"

## Key Features

- Cost overrun prediction
- Schedule delay prediction
- Project-level risk scoring
- Explainable risk factors
- Sector-wise analytics
- State-wise analytics
- Agency-wise analytics
- Project benchmarking
- Interactive monitoring dashboard
- Early-warning indicators

## System Architecture

```text
PAIMANA DATA
      │
      ▼
DATA EXTRACTION & CLEANING
      │
      ▼
FEATURE ENGINEERING
      │
      ├───────────────┐
      ▼               ▼
COST PREDICTION   TIME PREDICTION
      │               │
      └───────┬───────┘
              ▼
         RISK ENGINE
              │
              ▼
        EXPLAINABILITY
              │
              ▼
          DASHBOARD

## Tech Stack

### Data Processing
- Python
- Pandas
- NumPy
- PyMuPDF / pdfplumber

### Machine Learning
- scikit-learn
- XGBoost
- SHAP

### Dashboard & Visualization
- Streamlit
- Plotly
- PyDeck

### Development
- Git
- GitHub
- AI-assisted development tools

## Data

PREDIX uses publicly available PAIMANA project-monitoring reports containing project-level information such as:

- Project identifiers
- Project name
- Implementing agency
- State
- Approval/start date
- Original and revised commissioning dates
- Original and revised project cost
- Cumulative expenditure
- Physical progress

The available PAIMANA reports are used as the basis for data extraction, preprocessing, analysis and modelling.

## Project Structure

```text
PREDIX/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│
├── src/
│   ├── data/
│   ├── models/
│   │   ├── cost/
│   │   └── time/
│   ├── risk/
│   ├── analytics/
│   └── app/
│
├── notebooks/
├── scripts/
├── tests/
│
├── README.md
├── CONTRIBUTING.md
└── requirements.txt

Development Philosophy

PREDIX follows a modular architecture so that data processing, prediction, risk assessment, analytics and visualization can be developed independently and integrated through clearly defined interfaces.

AI coding tools may be used during development, but generated code must be reviewed, tested and understood by the contributor responsible for it.

Disclaimer

PREDIX is a prototype decision-support system developed for Smart India Hackathon 2026.
