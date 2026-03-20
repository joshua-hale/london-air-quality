import io
import logging
import boto3
import joblib
from typing import Dict, List
from config.config import settings

logger = logging.getLogger(__name__)

POLLUTANTS = ["pm2_5", "pm10", "no2", "o3", "so2", "european_aqi"]
HORIZONS = ["4h", "8h"]

def _get_s3_client():
    """Return boto3 client pointed at MinIO locally or real AWS in production."""
    if settings.s3_endpoint_url:
        return boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin"
        )
    return boto3.client("s3")

def _load_artifact(key: str):
    """Load a single joblib artifact from S3 into memory."""
    s3 = _get_s3_client()
    buffer = io.BytesIO()
    s3.download_fileobj(settings.s3_bucket, key, buffer)
    buffer.seek(0)
    return joblib.load(buffer)

def load_models() -> Dict:
    """Load all 12 models from S3. Returns dict keyed by pollutant_horizon."""
    models = {}
    for pollutant in POLLUTANTS:
        for horizon in HORIZONS:
            key = f"models/{pollutant}/{pollutant}_{horizon}.pkl"
            models[f"{pollutant}_{horizon}"] = _load_artifact(key)
            logger.info(f"Loaded model: {key}")
    return models

def load_borough_map() -> Dict:
    """Load borough encoding map from S3."""
    return _load_artifact("models/borough_map.pkl")

def load_feature_columns() -> List[str]:
    """Load feature column order from S3."""
    return _load_artifact("models/feature_columns.pkl")