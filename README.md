# London Air Pollution Intelligence

Real-time air quality monitoring and ML-powered forecasting 
for all 33 London boroughs.

## Live Application
https://london-air-pollution.com

## API Documentation  
http://london-air-quality-dev-alb-1219433375.eu-west-2.elb.amazonaws.com/docs#/](http://london-air-quality-dev-alb-1219433375.eu-west-2.elb.amazonaws.com/docs#/

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

All models trained on 580,000+ hourly readings across 33 London boroughs (Feb 2023 — Feb 2026).
Temporal train/test split at Feb 2025 to prevent data leakage.

| Model | Horizon | MAE | RMSE | R2 |
|---|---|---|---|---|
| European AQI | 4h | 2.35 | 3.09 | 0.902 |
| European AQI | 8h | 3.18 | 4.08 | 0.829 |
| PM2.5 | 4h | 1.72 | 2.62 | 0.839 |
| PM2.5 | 8h | 2.55 | 3.86 | 0.651 |
| PM10 | 4h | 2.38 | 3.40 | 0.792 |
| PM10 | 8h | 3.41 | 4.84 | 0.580 |
| NO2 | 4h | 4.56 | 6.61 | 0.789 |
| NO2 | 8h | 6.31 | 9.10 | 0.600 |
| O3 | 4h | 7.44 | 9.65 | 0.823 |
| O3 | 8h | 10.45 | 13.21 | 0.669 |
| SO2 | 4h | 0.53 | 0.84 | 0.762 |
| SO2 | 8h | 0.76 | 1.17 | 0.547 |

MAE and RMSE units: μg/m³ (European AQI is dimensionless index)

All 4h models achieve R2 > 0.75. Performance degrades at 8h as expected
for atmospheric prediction — SO2 and PM10 at 8h are acknowledged limitations
due to the episodic nature of these pollutants in urban environments.
