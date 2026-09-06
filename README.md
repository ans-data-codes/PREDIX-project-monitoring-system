# PREDIX-project-monitoring-system

### AI-Powered Predictive Infrastructure Monitoring & Early Warning System

> **PAIMANA tells us what is happening. PREDIX tells us what is likely to happen next.**

## Overview

PREDIX is an AI-powered decision-support platform designed to help monitor large Central Sector infrastructure projects and identify potential cost overruns, schedule delays, and implementation risks before they materialize.

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
