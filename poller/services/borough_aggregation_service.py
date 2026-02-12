from typing import List, Dict
from poller.models.individualborough import IndividualBorough
from poller.models.monitoring_point import MonitoringPoint

def borough_aggregation_service(points: List[MonitoringPoint]) -> List[IndividualBorough]:
    """Aggregate monitoring point data by borough"""

    