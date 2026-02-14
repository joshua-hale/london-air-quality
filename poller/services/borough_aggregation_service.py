from typing import List, Dict
from models.individualborough import IndividualBorough
from models.monitoring_point import MonitoringPoint

def borough_aggregator(points: List[MonitoringPoint]) -> List[IndividualBorough]:
    """Aggregate monitoring point data by borough"""

    # Build dictionary of monitoring points grouped by borough 
    borough_groups = {}
    for point in points:
        if point.borough not in borough_groups:
            borough_groups[point.borough] = []
        borough_groups[point.borough].append(point)

    # List to hold average PM2.5 per borough (Later all metrics)
    borough_aggregation = []

    for borough_name in borough_groups.keys():
        borough_points = borough_groups[borough_name]

        # Get list of PM2.5 values for all points in borough
        pm25_values = [point.pm2_5 for point in borough_points if point.pm2_5 is not None]

        # Skip processing this borough if no PM2.5 values (CHANGE LATER WHEN MORE ADDING MORE METRICS)
        if len(pm25_values) == 0:
            continue

        # Get borough average PM2.5 values
        total = 0
        for value in pm25_values:
            total += value
        avg_pm25 = total / len(pm25_values)

        # Get latest timestamp
        latest_timestamp = borough_points[0].timestamp
        for point in borough_points:
            if point.timestamp > latest_timestamp:
                latest_timestamp = point.timestamp

        # Create IndividualBorough object 
        borough = IndividualBorough(
            borough_name=borough_name,
            avg_pm_25=avg_pm25,
            last_updated=latest_timestamp
        )

        # Append IndividualBorough object to borough_aggregation list
        borough_aggregation.append(borough)

    # Sort by borough name
    borough_aggregation.sort(key=lambda b: b.borough_name)

    return borough_aggregation