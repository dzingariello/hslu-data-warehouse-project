import json
import requests
import boto3
import os
import psycopg2

ENDPOINT = os.environ['ENDPOINT']
DB_NAME = os.environ['DB_NAME']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

destination_api_key = 'HFjqHMLW8y8HdSOUjKBfL9JZYPQo5Rvo3Qq1yk3z'
location_api_key = 'AhxU1TpHSGQtGn7LTJyhZFdvHo-DujmZRmBarW5YqZ-ez_Rx-oWAooP6JBmizGzI'
destination_api_url = 'https://opendata.myswitzerland.io/v1/destinations/?hitsPerPage=50&striphtml=true'

API_GEO = "https://dev.virtualearth.net/REST/v1/Locations/"
location_data = {}

def lambda_handler(event, context):
    #retrieving destinations via mySwitzerland API
    headers = {
        "accept": "application/json",
        "x-api-key": destination_api_key
    }

    destination_list = []

    for page in range(20): #sometimes if fails due to the large number here, might try smaller (e.g. 5), or just rerun
        url = f"{destination_api_url}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for entry in data['data']:
                name = entry.get('name', None)
                geo = entry.get('geo', {})
                latitude = geo.get('latitude', None)
                longitude = geo.get('longitude', None)
                classifications = entry.get('classification', [])

                classification_list = []

                for classification in classifications:
                    classification_name = classification.get('name', None)
                    classification_values = classification.get('values', [])

                    for value in classification_values:
                        value_name = value.get('name', None)
                        value_title = value.get('title', None)

                        classification_list.append({
                            "classification_name": classification_name,
                            "value_name": value_name,
                            "value_title": value_title
                        })

                destination_dict = {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "classifications": classification_list
                }

                destination_list.append(destination_dict)
        else:
            print("Failed to retrieve data")
            
    ###########################################################################
    #retrieving corresponding locations
    
    for destination in destination_list:
        name = destination['name']
        latitude = destination['latitude']
        longitude = destination['longitude']
        api_url = f"{API_GEO}{latitude},{longitude}?key={location_api_key}"
        response = requests.get(api_url)

        if response.status_code == 200:
            geo_data = response.json()

            if 'resourceSets' in geo_data and len(geo_data['resourceSets']) > 0:
                resource = geo_data['resourceSets'][0]['resources'][0]
                canton = resource.get('address', {}).get('adminDistrict', 'Unknown')
                municipality = resource.get('address', {}).get('adminDistrict2', 'Unknown')

                if canton not in location_data:
                    location_data[canton] = {}

                if municipality not in location_data[canton]:
                    location_data[canton][municipality] = []

                location_data[canton][municipality].append(name)
            else:
                print(f"Failed to retrieve data for {name}")
        else:
            print(f"Failed to retrieve data for {name}")

    location_list = []

    for canton, municipalities in location_data.items():
        for municipality, destinations in municipalities.items():
            location_dict = {
                "municipality": municipality,
                "canton": canton,
                "destinations": destinations
            }
            location_list.append(location_dict)
    
    ############################################################################        
    #Load into S3 bucket
    #S3 configuration
    s3_bucket_name = 'switzerlandtourismbucket'
    s3_object_dest = 'destinations.json'
    s3_object_loc = 'locations.json'
    
    
    # Initialize the S3 client
    s3 = boto3.client('s3')
    
    # Upload the API response to S3
    s3.put_object(Body=json.dumps(destination_list), Bucket=s3_bucket_name, Key=s3_object_dest)
    s3.put_object(Body=json.dumps(location_list), Bucket=s3_bucket_name, Key=s3_object_loc)

    return location_list[0]
    
    
    
    
    
    
    
    
