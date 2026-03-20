# London Air Pollution Intelligence

Real-time air quality monitoring and ML-powered forecasting 
for all 33 London boroughs.

## Live Application
https://london-air-pollution.com

## API Documentation  
https://london-air-pollution.com/docs](http://london-air-quality-dev-alb-1219433375.eu-west-2.elb.amazonaws.com/docs#/

## Architecture Overview
Brief description + link to architecture diagram

## Project Structure
london-air-quality/
  api/          FastAPI service — serves Redis cached predictions
  poller/       Ingestion service — fetches Open-Meteo data hourly
  pipeline/     ML pipeline — feature engineering + LightGBM inference
  frontend/     React application — map and charts views
  terraform/    Infrastructure as code — AWS ECS, Redis, CloudFront
  ml/           Model training scripts and feature engineering


## Technology Stack
- FastAPI + Redis — sub-10ms API responses via precomputed predictions
- LightGBM — 18 models across 6 pollutants and 2 horizons
- AWS ECS Fargate — containerised hourly pipeline
- Terraform — full infrastructure as code
- React + Leaflet — interactive borough heatmap

## Model Performance
| Model | R2 | MAE |
|---|---|---|
| European AQI 4h | 0.902 | 2.35 |
| PM2.5 4h | 0.839 | 1.72 |
| ... | ... | ... |
