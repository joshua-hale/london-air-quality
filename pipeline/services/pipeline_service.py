import logging
import s3fs
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List
from data.borough_data import LONDON_MONITORING_POINTS
from services.feature_engineering_service import build_features_for_serving, POLLUTANTS
from services.model_service import load_models, load_borough_map, load_feature_columns
from services.prediction_cache_service import write_predictions_to_redis, write_pipeline_status
from models.borough_4h import Borough_4h
from models.borough_8h import Borough_8h
from config.config import settings

logger = logging.getLogger(__name__)

HORIZONS = ["4h", "8h"]


def _get_filesystem() -> s3fs.S3FileSystem:
    """Return S3FileSystem pointed at MinIO locally or real AWS in production."""
    if settings.s3_endpoint_url:
        return s3fs.S3FileSystem(
            endpoint_url=settings.s3_endpoint_url,
            key=settings.aws_access_key_id,
            secret=settings.aws_secret_access_key
        )
    return s3fs.S3FileSystem()


fs = _get_filesystem()



def load_borough_window(borough: str) -> pd.DataFrame:
    """Load 50h window from S3 parquet for a single borough."""

    path = f"s3://{settings.s3_bucket}/data/backfill/{borough}.parquet"
    df = pd.read_parquet(path, filesystem=fs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=50)
    return df[df["timestamp"] >= cutoff].sort_values("timestamp").reset_index(drop=True)


def run_borough_inference(
    borough: str,
    location: Dict,
    models: Dict,
    borough_map: Dict,
    feature_cols: List[str],
    run_timestamp: datetime
) -> Dict:
    """
    Load S3 window, engineer features, run inference for one borough.
    Returns validated and serialised 4h and 8h prediction dicts.
    """

    # Load 50h window from S3
    df = load_borough_window(borough)

    if len(df) < 48:
        logger.warning(f"Insufficient history for {borough} ({len(df)} rows) — skipping")
        return None

    # Engineer features using same function as training
    features_df = build_features_for_serving(df, borough_map)

    if features_df.empty:
        logger.warning(f"Empty features for {borough} — skipping")
        return None

    # Take latest row and build input in exact training column order
    latest_row = features_df.iloc[-1]
    X = pd.DataFrame([[float(latest_row[col]) for col in feature_cols]], columns=feature_cols)

    # Run inference for all pollutants and horizons
    raw = {}
    for pollutant in POLLUTANTS:
        for horizon in HORIZONS:
            key = f"{pollutant}_{horizon}"
            raw[key] = round(float(models[key].predict(X)[0]), 2)

    # Validate through pydantic models raise if any value fails field constraints
    prediction_4h = Borough_4h(
        borough=borough,
        latitude=location["lat"],
        longitude=location["lon"],
        timestamp=run_timestamp,
        pm2_5=raw["pm2_5_4h"],
        pm10=raw["pm10_4h"],
        no2=raw["no2_4h"],
        o3=raw["o3_4h"],
        so2=raw["so2_4h"],
        european_aqi=raw["european_aqi_4h"],
    )

    prediction_8h = Borough_8h(
        borough=borough,
        latitude=location["lat"],
        longitude=location["lon"],
        timestamp=run_timestamp,
        pm2_5=raw["pm2_5_8h"],
        pm10=raw["pm10_8h"],
        no2=raw["no2_8h"],
        o3=raw["o3_8h"],
        so2=raw["so2_8h"],
        european_aqi=raw["european_aqi_8h"],
    )

    return {
        "4h": prediction_4h.model_dump(),
        "8h": prediction_8h.model_dump()
    }


def run_pipeline() -> Dict:
    """
    Load models and artifacts from S3.
    Run inference for all boroughs.
    Write 4h and 8h prediction arrays to Redis.
    """

    write_pipeline_status("running")
    failed = []

    # Capture pipeline run timestamp once and share across all boroughs
    run_timestamp = datetime.now(timezone.utc)

    # Load all artifacts once — shared across all borough runs
    logger.info("Loading models and artifacts from S3...")
    models = load_models()
    borough_map = load_borough_map()
    feature_cols = load_feature_columns()
    logger.info(f"Loaded {len(models)} models, {len(feature_cols)} feature columns")

    # Collect all borough predictions before writing to Redis
    all_predictions = {"4h": [], "8h": []}

    for location in LONDON_MONITORING_POINTS:
        borough = location["borough"]
        try:
            result = run_borough_inference(
                borough, location, models, borough_map, feature_cols, run_timestamp
            )

            if result is None:
                failed.append(borough)
                continue

            all_predictions["4h"].append(result["4h"])
            all_predictions["8h"].append(result["8h"])

            logger.info(f"Inference complete for {borough}")

        except Exception as e:
            logger.error(f"Inference failed for {borough}: {e}", exc_info=True) 
            failed.append(borough)

    # Write both arrays to Redis in one operation only if we have predictions
    if all_predictions["4h"]:
        write_predictions_to_redis(all_predictions)
        logger.info(f"Cached predictions for {len(all_predictions['4h'])} boroughs")
    else:
        logger.error("No predictions generated — Redis not updated this run")

    if failed:
        logger.warning(f"Pipeline completed with {len(failed)} failures: {failed}")
        write_pipeline_status(f"partial — {len(failed)} boroughs failed")
    else:
        write_pipeline_status("ok")
        logger.info("Pipeline completed successfully")

    return {
        "boroughs_processed": len(all_predictions["4h"]),
        "boroughs_failed": len(failed),
        "failed": failed
    }