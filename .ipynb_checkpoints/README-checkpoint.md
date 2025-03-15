# Power Outage Prediction
Power Outage Prediction
Overview
This repository contains a machine learning model designed to predict power outages and their correlation with rare weather events. The project aims to analyze how different extreme weather conditions affect power infrastructure and develop a robust predictive system to anticipate outages.
Problem Statement
The goal is to build a model that can accurately predict power outages based on weather data, with a specific focus on rare or extreme weather events. The project examines the relationship between various meteorological phenomena and subsequent power disruptions.
Datasets
The analysis primarily utilizes two datasets:

Storm Event Dataset - Contains records of various weather events
Power Outage Dataset - Records of power disruptions and their details

Additional meteorological data sources:

NOAA public datasets
ERA5 comprehensive weather dataset (available from Copernicus Climate Data Store)
WeatherBench2 resources

Key Insights

Not all weather events have equal impact on power infrastructure
Multiple weather events often occur together, creating compound effects
Power outages typically exhibit a time lag following weather events
Initial analysis shows strong regional patterns (Texas-specific data is being evaluated for broader applicability)

Methodology

Classification approach with potential for multi-class analysis
Random Forest as baseline model
Evaluation on unseen data to ensure robust performance
Exploration of clustering approaches to identify distinct outage patterns
