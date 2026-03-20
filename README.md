# London Air Pollution Intelligence

Real-time air quality monitoring and ML-powered forecasting 
for all 33 London boroughs.

## Live Application
https://london-air-pollution.com

## API Documentation  
http://london-air-quality-dev-alb-1219433375.eu-west-2.elb.amazonaws.com/docs#/](http://london-air-quality-dev-alb-1219433375.eu-west-2.elb.amazonaws.com/docs#/

## Architecture 
```
┌─────────────────────────────────────────────────────────────────────┐
│                      EVENTBRIDGE SCHEDULERS                          │
│  • Hourly: Data Ingestion Pipeline                                  │
│  • Hourly: ML Prediction Pipeline                                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ECS FARGATE                                 │
│                                                                      │
│  ┌────────────────────────────┐  ┌────────────────────────────────┐ │
│  │     Ingestion Poller       │  │     ML Prediction Pipeline     │ │
│  │                            │  │                                │ │
│  │  • Fetch weather data      │  │  • Read Parquet from S3        │ │
│  │  • Fetch pollution data    │  │  • Engineer lag + rolling      │ │
│  │    (Open-Meteo API)        │  │    features (48h window)       │ │
│  │  • Write Parquet → S3      │  │  • Run 12 LightGBM models      │ │
│  │  • Write current → Redis   │  │    (6 pollutants × 2 horizons) │ │
│  │  • 33 boroughs, hourly     │  │  • Write predictions → Redis   │ │
│  │  • Terminates on complete  │  │  • ~1 min/hour, then exits     │ │
│  └────────────────────────────┘  └────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │           Stateless API Service  (2 replicas)                │   │
│  │                                                              │   │
│  │  GET /boroughs              GET /boroughs/{id}               │   │
│  │  GET /predictions/12h       GET /predictions/24h             │   │
│  │                                                              │   │
│  │  • 2 × 0.25 vCPU Fargate (~£5/mo compute)                   │   │
│  │  • Zero inference at request time — Redis reads only         │   │
│  │  • Distributed rate limiting via Redis                       │   │
│  │  • ETag validation + CDN caching                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                               │
│                                                                      │
│  ┌─────────────────────┐  ┌──────────────────────┐  ┌────────────┐ │
│  │  ElastiCache Redis  │  │   S3 — Data Lake     │  │ S3 Models  │ │
│  │                     │  │                      │  │            │ │
│  │  • Current data     │  │  • Parquet files     │  │  • 12 ×    │ │
│  │  • 12h predictions  │  │  • 580,000+ records  │  │  LightGBM  │ │
│  │  • 24h predictions  │  │  • Feb 2023–present  │  │  models    │ │
│  │  • Rate limit state │  │  • Ground truth      │  │            │ │
│  │  • TTL: 24 hours    │  │    store             │  │  • feature │ │
│  │                     │  │                      │  │  _columns  │ │
│  │  Ephemeral cache —  │  │  Restores Redis on   │  │  .pkl      │ │
│  │  S3 is source of    │  │  cold start or       │  │            │ │
│  │  truth              │  │  pipeline failure    │  │  • borough │ │
│  └─────────────────────┘  └──────────────────────┘  │  _map.pkl  │ │
│                                                      └────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOAD BALANCER                         │
│  • Health checks across ECS replicas                                │
│  • SSL termination                                                  │
│  • Traffic distribution                                             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUDFRONT CDN                               │
│  • Edge caching (5-min TTL)                                         │
│  • ETag validation                                                  │
│  • HTTPS termination                                                │
│  • Global distribution                                              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              REACT FRONTEND  (S3 + CloudFront static hosting)        │
│                                                                      │
│  ┌──────────────────────────────┐  ┌───────────────────────────┐   │
│  │       Leaflet Map            │  │     Data Views            │   │
│  │                              │  │                           │   │
│  │  • Borough-level heatmap     │  │  • Recharts forecast      │   │
│  │  • 12h + 24h overlays        │  │    comparison charts      │   │
│  │  • Interactive popups        │  │  • Multi-pollutant table  │   │
│  │  • Colour-coded AQI bands    │  │  • WHO threshold context  │   │
│  └──────────────────────────────┘  └───────────────────────────┘   │
│                                                                      │
│                   london-air-pollution.com                           │
└─────────────────────────────────────────────────────────────────────┘

Infrastructure: Terraform (8 modules) · Docker + ECR · Route 53 + ACM
```

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
