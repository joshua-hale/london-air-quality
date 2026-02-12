"""
Monitoring point selection strategy:
1. High Traffic - Major road or commercial center (highest pollution)
2. Residential - Typical residential area (medium pollution)
3. Green Space - Park or low-traffic area (lowest pollution, baseline)

This creates good gradient variation for visualization.
"""

LONDON_MONITORING_POINTS = [
    # ========== Inner London ==========
    
    # 1. City of London
    {"name": "City - Bank Junction", "lat": 51.5134, "lon": -0.0889, "borough": "City of London", "type": "high_traffic"},
    {"name": "City - Barbican", "lat": 51.5203, "lon": -0.0938, "borough": "City of London", "type": "residential"},
    {"name": "City - Postman's Park", "lat": 51.5170, "lon": -0.0975, "borough": "City of London", "type": "green_space"},
    
    # 2. Westminster
    {"name": "Westminster - Marylebone Road", "lat": 51.5226, "lon": -0.1546, "borough": "Westminster", "type": "high_traffic"},
    {"name": "Westminster - Pimlico", "lat": 51.4886, "lon": -0.1338, "borough": "Westminster", "type": "residential"},
    {"name": "Westminster - Hyde Park", "lat": 51.5073, "lon": -0.1657, "borough": "Westminster", "type": "green_space"},
    
    # 3. Kensington and Chelsea
    {"name": "K&C - Cromwell Road", "lat": 51.4946, "lon": -0.1782, "borough": "Kensington and Chelsea", "type": "high_traffic"},
    {"name": "K&C - South Kensington", "lat": 51.4941, "lon": -0.1750, "borough": "Kensington and Chelsea", "type": "residential"},
    {"name": "K&C - Holland Park", "lat": 51.5075, "lon": -0.2025, "borough": "Kensington and Chelsea", "type": "green_space"},
    
    # 4. Hammersmith and Fulham
    {"name": "H&F - Hammersmith Broadway", "lat": 51.4927, "lon": -0.2188, "borough": "Hammersmith and Fulham", "type": "high_traffic"},
    {"name": "H&F - Fulham", "lat": 51.4817, "lon": -0.1950, "borough": "Hammersmith and Fulham", "type": "residential"},
    {"name": "H&F - Bishops Park", "lat": 51.4748, "lon": -0.2053, "borough": "Hammersmith and Fulham", "type": "green_space"},
    
    # 5. Wandsworth
    {"name": "Wandsworth - Wandsworth Road", "lat": 51.4621, "lon": -0.1733, "borough": "Wandsworth", "type": "high_traffic"},
    {"name": "Wandsworth - Clapham Junction", "lat": 51.4642, "lon": -0.1703, "borough": "Wandsworth", "type": "residential"},
    {"name": "Wandsworth - Wandsworth Common", "lat": 51.4501, "lon": -0.1699, "borough": "Wandsworth", "type": "green_space"},
    
    # 6. Lambeth
    {"name": "Lambeth - Vauxhall Cross", "lat": 51.4864, "lon": -0.1242, "borough": "Lambeth", "type": "high_traffic"},
    {"name": "Lambeth - Brixton", "lat": 51.4613, "lon": -0.1157, "borough": "Lambeth", "type": "residential"},
    {"name": "Lambeth - Brockwell Park", "lat": 51.4534, "lon": -0.1089, "borough": "Lambeth", "type": "green_space"},
    
    # 7. Southwark
    {"name": "Southwark - Elephant & Castle", "lat": 51.4940, "lon": -0.0997, "borough": "Southwark", "type": "high_traffic"},
    {"name": "Southwark - Peckham", "lat": 51.4742, "lon": -0.0690, "borough": "Southwark", "type": "residential"},
    {"name": "Southwark - Burgess Park", "lat": 51.4813, "lon": -0.0822, "borough": "Southwark", "type": "green_space"},
    
    # 8. Tower Hamlets
    {"name": "Tower Hamlets - Whitechapel Road", "lat": 51.5193, "lon": -0.0604, "borough": "Tower Hamlets", "type": "high_traffic"},
    {"name": "Tower Hamlets - Bow", "lat": 51.5273, "lon": -0.0245, "borough": "Tower Hamlets", "type": "residential"},
    {"name": "Tower Hamlets - Victoria Park", "lat": 51.5361, "lon": -0.0376, "borough": "Tower Hamlets", "type": "green_space"},
    
    # 9. Hackney
    {"name": "Hackney - Hackney Road", "lat": 51.5321, "lon": -0.0632, "borough": "Hackney", "type": "high_traffic"},
    {"name": "Hackney - Dalston", "lat": 51.5461, "lon": -0.0750, "borough": "Hackney", "type": "residential"},
    {"name": "Hackney - London Fields", "lat": 51.5422, "lon": -0.0589, "borough": "Hackney", "type": "green_space"},
    
    # 10. Islington
    {"name": "Islington - Upper Street", "lat": 51.5381, "lon": -0.1032, "borough": "Islington", "type": "high_traffic"},
    {"name": "Islington - Barnsbury", "lat": 51.5451, "lon": -0.1135, "borough": "Islington", "type": "residential"},
    {"name": "Islington - Highbury Fields", "lat": 51.5486, "lon": -0.0986, "borough": "Islington", "type": "green_space"},
    
    # 11. Camden
    {"name": "Camden - Euston Road", "lat": 51.5257, "lon": -0.1348, "borough": "Camden", "type": "high_traffic"},
    {"name": "Camden - Kentish Town", "lat": 51.5518, "lon": -0.1404, "borough": "Camden", "type": "residential"},
    {"name": "Camden - Hampstead Heath", "lat": 51.5569, "lon": -0.1776, "borough": "Camden", "type": "green_space"},
    
    # ========== Outer London - North ==========
    
    # 12. Barnet
    {"name": "Barnet - High Barnet", "lat": 51.6503, "lon": -0.1988, "borough": "Barnet", "type": "high_traffic"},
    {"name": "Barnet - Finchley", "lat": 51.5919, "lon": -0.2060, "borough": "Barnet", "type": "residential"},
    {"name": "Barnet - Mill Hill Park", "lat": 51.6138, "lon": -0.2425, "borough": "Barnet", "type": "green_space"},
    
    # 13. Enfield
    {"name": "Enfield - Fore Street", "lat": 51.6518, "lon": -0.0804, "borough": "Enfield", "type": "high_traffic"},
    {"name": "Enfield - Edmonton", "lat": 51.6138, "lon": -0.0563, "borough": "Enfield", "type": "residential"},
    {"name": "Enfield - Broomfield Park", "lat": 51.6270, "lon": -0.1189, "borough": "Enfield", "type": "green_space"},
    
    # 14. Haringey
    {"name": "Haringey - Wood Green High Road", "lat": 51.5975, "lon": -0.1097, "borough": "Haringey", "type": "high_traffic"},
    {"name": "Haringey - Tottenham", "lat": 51.5883, "lon": -0.0722, "borough": "Haringey", "type": "residential"},
    {"name": "Haringey - Finsbury Park", "lat": 51.5647, "lon": -0.1065, "borough": "Haringey", "type": "green_space"},
    
    # 15. Waltham Forest
    {"name": "Waltham Forest - Walthamstow Central", "lat": 51.5830, "lon": -0.0195, "borough": "Waltham Forest", "type": "high_traffic"},
    {"name": "Waltham Forest - Leyton", "lat": 51.5607, "lon": -0.0068, "borough": "Waltham Forest", "type": "residential"},
    {"name": "Waltham Forest - Lloyd Park", "lat": 51.5891, "lon": -0.0173, "borough": "Waltham Forest", "type": "green_space"},
    
    # ========== Outer London - East ==========
    
    # 16. Redbridge
    {"name": "Redbridge - Ilford High Road", "lat": 51.5590, "lon": 0.0741, "borough": "Redbridge", "type": "high_traffic"},
    {"name": "Redbridge - South Woodford", "lat": 51.5914, "lon": 0.0275, "borough": "Redbridge", "type": "residential"},
    {"name": "Redbridge - Valentines Park", "lat": 51.5763, "lon": 0.0737, "borough": "Redbridge", "type": "green_space"},
    
    # 17. Barking and Dagenham
    {"name": "Barking - Barking Road", "lat": 51.5390, "lon": 0.0810, "borough": "Barking and Dagenham", "type": "high_traffic"},
    {"name": "Barking - Dagenham", "lat": 51.5481, "lon": 0.1488, "borough": "Barking and Dagenham", "type": "residential"},
    {"name": "Barking - Mayesbrook Park", "lat": 51.5447, "lon": 0.1271, "borough": "Barking and Dagenham", "type": "green_space"},
    
    # 18. Havering
    {"name": "Havering - Romford Road", "lat": 51.5779, "lon": 0.1821, "borough": "Havering", "type": "high_traffic"},
    {"name": "Havering - Hornchurch", "lat": 51.5589, "lon": 0.2178, "borough": "Havering", "type": "residential"},
    {"name": "Havering - Harrow Lodge Park", "lat": 51.5716, "lon": 0.2174, "borough": "Havering", "type": "green_space"},
    
    # 19. Newham
    {"name": "Newham - Stratford Broadway", "lat": 51.5416, "lon": -0.0022, "borough": "Newham", "type": "high_traffic"},
    {"name": "Newham - Forest Gate", "lat": 51.5496, "lon": 0.0255, "borough": "Newham", "type": "residential"},
    {"name": "Newham - West Ham Park", "lat": 51.5350, "lon": 0.0152, "borough": "Newham", "type": "green_space"},
    
    # ========== Outer London - South East ==========
    
    # 20. Greenwich
    {"name": "Greenwich - Woolwich Road", "lat": 51.4893, "lon": 0.0648, "borough": "Greenwich", "type": "high_traffic"},
    {"name": "Greenwich - Blackheath", "lat": 51.4656, "lon": 0.0048, "borough": "Greenwich", "type": "residential"},
    {"name": "Greenwich - Greenwich Park", "lat": 51.4769, "lon": -0.0005, "borough": "Greenwich", "type": "green_space"},
    
    # 21. Bexley
    {"name": "Bexley - Erith Road", "lat": 51.4822, "lon": 0.1788, "borough": "Bexley", "type": "high_traffic"},
    {"name": "Bexley - Bexleyheath", "lat": 51.4569, "lon": 0.1500, "borough": "Bexley", "type": "residential"},
    {"name": "Bexley - Danson Park", "lat": 51.4503, "lon": 0.1396, "borough": "Bexley", "type": "green_space"},
    
    # 22. Bromley
    {"name": "Bromley - Bromley High Street", "lat": 51.4055, "lon": 0.0146, "borough": "Bromley", "type": "high_traffic"},
    {"name": "Bromley - Orpington", "lat": 51.3727, "lon": 0.0982, "borough": "Bromley", "type": "residential"},
    {"name": "Bromley - Crystal Palace Park", "lat": 51.4213, "lon": -0.0735, "borough": "Bromley", "type": "green_space"},
    
    # 23. Lewisham
    {"name": "Lewisham - Lewisham High Street", "lat": 51.4643, "lon": -0.0146, "borough": "Lewisham", "type": "high_traffic"},
    {"name": "Lewisham - Catford", "lat": 51.4446, "lon": -0.0197, "borough": "Lewisham", "type": "residential"},
    {"name": "Lewisham - Ladywell Fields", "lat": 51.4567, "lon": -0.0226, "borough": "Lewisham", "type": "green_space"},
    
    # ========== Outer London - South ==========
    
    # 24. Croydon
    {"name": "Croydon - North End", "lat": 51.3762, "lon": -0.1025, "borough": "Croydon", "type": "high_traffic"},
    {"name": "Croydon - South Croydon", "lat": 51.3594, "lon": -0.0925, "borough": "Croydon", "type": "residential"},
    {"name": "Croydon - Lloyd Park", "lat": 51.3832, "lon": -0.0974, "borough": "Croydon", "type": "green_space"},
    
    # 25. Sutton
    {"name": "Sutton - High Street", "lat": 51.3618, "lon": -0.1945, "borough": "Sutton", "type": "high_traffic"},
    {"name": "Sutton - Carshalton", "lat": 51.3665, "lon": -0.1677, "borough": "Sutton", "type": "residential"},
    {"name": "Sutton - Beddington Park", "lat": 51.3831, "lon": -0.1424, "borough": "Sutton", "type": "green_space"},
    
    # 26. Merton
    {"name": "Merton - Morden Road", "lat": 51.4017, "lon": -0.1949, "borough": "Merton", "type": "high_traffic"},
    {"name": "Merton - Wimbledon", "lat": 51.4214, "lon": -0.2064, "borough": "Merton", "type": "residential"},
    {"name": "Merton - Wimbledon Common", "lat": 51.4309, "lon": -0.2362, "borough": "Merton", "type": "green_space"},
    
    # 27. Kingston upon Thames
    {"name": "Kingston - Kingston Road", "lat": 51.4085, "lon": -0.3064, "borough": "Kingston upon Thames", "type": "high_traffic"},
    {"name": "Kingston - Surbiton", "lat": 51.3926, "lon": -0.3068, "borough": "Kingston upon Thames", "type": "residential"},
    {"name": "Kingston - Richmond Park (Kingston Gate)", "lat": 51.4264, "lon": -0.2857, "borough": "Kingston upon Thames", "type": "green_space"},
    
    # 28. Richmond upon Thames
    {"name": "Richmond - Kew Road", "lat": 51.4614, "lon": -0.2870, "borough": "Richmond upon Thames", "type": "high_traffic"},
    {"name": "Richmond - Twickenham", "lat": 51.4501, "lon": -0.3332, "borough": "Richmond upon Thames", "type": "residential"},
    {"name": "Richmond - Richmond Park", "lat": 51.4479, "lon": -0.2838, "borough": "Richmond upon Thames", "type": "green_space"},
    
    # ========== Outer London - West ==========
    
    # 29. Hounslow
    {"name": "Hounslow - Great West Road", "lat": 51.4746, "lon": -0.3580, "borough": "Hounslow", "type": "high_traffic"},
    {"name": "Hounslow - Brentford", "lat": 51.4875, "lon": -0.3107, "borough": "Hounslow", "type": "residential"},
    {"name": "Hounslow - Gunnersbury Park", "lat": 51.4927, "lon": -0.2806, "borough": "Hounslow", "type": "green_space"},
    
    # 30. Ealing
    {"name": "Ealing - Uxbridge Road", "lat": 51.5130, "lon": -0.3055, "borough": "Ealing", "type": "high_traffic"},
    {"name": "Ealing - Acton", "lat": 51.5089, "lon": -0.2674, "borough": "Ealing", "type": "residential"},
    {"name": "Ealing - Walpole Park", "lat": 51.5145, "lon": -0.3043, "borough": "Ealing", "type": "green_space"},
    
    # 31. Hillingdon
    {"name": "Hillingdon - Uxbridge Road (Hayes)", "lat": 51.5134, "lon": -0.4209, "borough": "Hillingdon", "type": "high_traffic"},
    {"name": "Hillingdon - Ruislip", "lat": 51.5735, "lon": -0.4232, "borough": "Hillingdon", "type": "residential"},
    {"name": "Hillingdon - Ruislip Woods", "lat": 51.5854, "lon": -0.4363, "borough": "Hillingdon", "type": "green_space"},
    
    # 32. Harrow
    {"name": "Harrow - Station Road", "lat": 51.5898, "lon": -0.3346, "borough": "Harrow", "type": "high_traffic"},
    {"name": "Harrow - Wealdstone", "lat": 51.5944, "lon": -0.3350, "borough": "Harrow", "type": "residential"},
    {"name": "Harrow - Pinner Park", "lat": 51.5951, "lon": -0.3820, "borough": "Harrow", "type": "green_space"},
    
    # 33. Brent
    {"name": "Brent - Wembley High Road", "lat": 51.5519, "lon": -0.2981, "borough": "Brent", "type": "high_traffic"},
    {"name": "Brent - Willesden", "lat": 51.5492, "lon": -0.2432, "borough": "Brent", "type": "residential"},
    {"name": "Brent - Gladstone Park", "lat": 51.5615, "lon": -0.2333, "borough": "Brent", "type": "green_space"},
]

# Helper to get points by borough
def get_points_by_borough(borough_name: str):
    """Get all monitoring points for a specific borough"""
    return [p for p in LONDON_MONITORING_POINTS if p["borough"] == borough_name]

# Helper to get all borough names
def get_all_boroughs():
    """Get list of all unique boroughs"""
    return sorted(list(set(p["borough"] for p in LONDON_MONITORING_POINTS)))