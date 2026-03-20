import logging
import sys
import time
from services.pipeline_service import run_pipeline

logger = logging.getLogger(__name__)

def main():
    """ML prediction pipeline with retry handling."""

    MAX_RETRIES = 3
    RETRY_DELAY = 60

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = run_pipeline()

            logger.info("Pipeline execution completed successfully!")
            logger.info(f"Result: {result}")
            logger.info(f"Attempts needed: {attempt}")

            sys.exit(0)

        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning(
                    f"Pipeline failed (attempt {attempt}/{MAX_RETRIES}): {e}. "
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.exception(f"Pipeline failed: All {MAX_RETRIES} attempts failed")
                sys.exit(1)

if __name__ == "__main__":
    main()