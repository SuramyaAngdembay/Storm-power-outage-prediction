# Power Outage Prediction

## Overview

This repository contains a machine learning model designed to predict power outages and analyze their correlation with rare weather events. The project aims to evaluate how different extreme weather conditions affect power infrastructure and develop a robust predictive system to anticipate outages.

## Problem Statement

The goal is to build a model that accurately predicts power outages based on weather data, with a specific focus on rare or extreme weather events. The project investigates the relationship between various meteorological phenomena and subsequent power disruptions.

## Datasets

### Primary Datasets
- **Storm Event Dataset:** Contains records of various weather events.
- **Power Outage Dataset:** Records details of power disruptions.

### Additional Meteorological Data Sources
- NOAA public datasets
- ERA5 comprehensive weather dataset (available from the Copernicus Climate Data Store)
- WeatherBench2 resources

## Key Insights

- **Impact Variability:** Not all weather events affect power infrastructure equally.
- **Compound Effects:** Multiple weather events can occur simultaneously, creating compound impacts.
- **Time Lag:** Power outages typically occur after a delay following weather events.
- **Regional Patterns:** Initial analysis shows strong regional patterns, with Texas-specific data under evaluation for broader applicability.

## Methodology

- **Approach:** Classification with potential for multi-class analysis.
- **Baseline Model:** Random Forest.
- **Evaluation:** Testing on unseen data to ensure robust performance.
- **Exploratory Analysis:** Investigation of clustering techniques to identify distinct outage patterns.
