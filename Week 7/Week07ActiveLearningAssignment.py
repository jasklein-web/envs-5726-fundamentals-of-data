import csv
import requests
import urllib.parse
import time

with open('/Users/jasonklein/Downloads/USEIA_Petroleum_Refineries_By_Nearest_Major_City.csv', 'r') as file:
    reader = csv.DictReader(file)
    rows = list(reader)

fema_url = 'https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query'

for row in rows:
    lat = row['Latitude']
    lon = row['Longitude']

    query = {
        'geometry': f'{lon},{lat}',
        'geometryType': 'esriGeometryPoint',
        'inSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'ZONE_SUBTY',
        'returnGeometry': 'false',
        'f': 'pjson'
    }

    encoded_query = urllib.parse.urlencode(query)
    full_url = fema_url + '?' + encoded_query

    try:
        response = requests.get(full_url)
        data = response.json()

        if 'features' in data and len(data['features']) > 0:
            hazard_zone = data['features'][0]['attributes']['ZONE_SUBTY']
            if hazard_zone:
                row['FEMA_Hazard_Zone'] = hazard_zone
            else:
                row['FEMA_Hazard_Zone'] = 'No Data'
        else:
            row['FEMA_Hazard_Zone'] = 'No Data'
    except:
        row['FEMA_Hazard_Zone'] = 'No Data'

    time.sleep(0.1)

for row in rows:
    origin_lat = row['Latitude']
    origin_lon = row['Longitude']
    dest_lat = row['NearestMajorCity_Latitude']
    dest_lon = row['NearestMajorCity_Longitude']

    osrm_url = f'http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?steps=false'

    try:
        response = requests.get(osrm_url)
        data = response.json()

        if 'routes' in data and len(data['routes']) > 0:
            row['DriveDuration_Seconds'] = data['routes'][0]['duration']
        else:
            row['DriveDuration_Seconds'] = 'No Data'
    except:
        row['DriveDuration_Seconds'] = 'No Data'

    time.sleep(0.1)

fieldnames = reader.fieldnames + ['FEMA_Hazard_Zone', 'DriveDuration_Seconds']

with open('/Users/jasonklein/Downloads/USEIA_Petroleum_Refineries_Updated.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)