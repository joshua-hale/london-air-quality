import logging
import sys
import time
from services.poller_service import run_poller

logger = logging.getLogger(__name__)

def main():
    """Main poller method to fetch air quality data and write to redis cache with retry handling"""

    MAX_RETRIES = 3
    RETRY_DELAY = 60
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            points_count, borough_count = run_poller()

            logger.info("Poller execution completed successfully!")
            logger.info(f"Monitoring points: {points_count}")
            logger.info(f"Boroughs: {borough_count}")
            logger.info(f"Attempts needed: {attempt}")

            sys.exit(0)

        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning(
                    f"Poller failed (attempt {attempt}/{MAX_RETRIES}): {e}. "
                f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.exception(f"Poller failed: All {MAX_RETRIES} attempts failed")
                sys.exit(1)

if __name__ == "__main__":
    main()