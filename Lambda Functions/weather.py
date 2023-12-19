import json
import requests
import os
import time
import boto3
import psycopg2

ENDPOINT = os.environ['ENDPOINT']
DB_NAME = os.environ['DB_NAME']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

def lambda_handler(event, context):
    object_key = 'destinations.json'
    temp_file_path = '/tmp/destinations.json'
    bucket_name = 'switzerlandtourismbucket'
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_key, temp_file_path)
    
    with open(temp_file_path, 'r') as temp_file:
        destination_list = json.load(temp_file)
    
    os.remove(temp_file_path)
    
    selected_names = ['Arosa', 'Wildhaus', 'Pfannenstiel', 'Meggen', 'Hallwil', 'Vermes', 'Grenchen', 'Spiez', 'Le Locle', 'Vevey', 'Bulle', 'Tenero', 'Geneva']
    selected_destinations = [destination for destination in destination_list if destination['name'] in selected_names]
    
    # Define a list to store information for each city
    all_cities_data = []

    # Loop through each entry in destination_list
    for destination in selected_destinations:
        latitude = destination['latitude']
        longitude = destination['longitude']
        # Skip the API call if latitude or longitude is None
        if latitude is None or longitude is None:
            continue

        # Update the URL with latitude and longitude from the current entry
        url_CH = f'http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid=127619cee40c71033954846a9bfcf283'

        api_response = requests.get(url_CH)
        api_data = api_response.json()

        # Extract information for the current city
        city_data = {
            'city': api_data.get('city', {}).get('name'),
            'lon': api_data.get('city', {}).get('coord', {}).get('lon'),
            'lat': api_data.get('city', {}).get('coord', {}).get('lat'),
            'main_temps': [],
            'main_temp_min': [],
            'main_temp_max': [],
            'main_humidity': [],
            'weather_main': [],
            'weather_description': [],
            'clouds': [],
            'wind': [],
            'visibility': [],
            'precipitation': [],
            'rain': [],
            'snow': [],
            'datetime': []
        }

        # Loop through entries in api_data['list'] and extract relevant information
        for i, entry in enumerate(api_data['list']):
            if i % 8 == 0:  # select 1 value every 24 hours
                city_data['main_temps'].append(entry['main'].get('temp'))
                city_data['main_temp_min'].append(entry['main'].get('temp_min'))
                city_data['main_temp_max'].append(entry['main'].get('temp_max'))
                city_data['main_humidity'].append(entry['main'].get('humidity'))
                for weather_condition in entry['weather']:
                    city_data['weather_main'].append(weather_condition.get('main'))
                    city_data['weather_description'].append(weather_condition.get('description'))
                city_data['clouds'].append(entry.get('clouds', {}).get('all'))
                city_data['wind'].append(entry.get('wind', {}).get('speed'))
                city_data['visibility'].append(entry.get('visibility'))
                city_data['precipitation'].append(entry.get('pop'))
                city_data['rain'].append(entry.get('rain', {}).get('3h'))
                city_data['snow'].append(entry.get('snow', {}).get('3h'))
                city_data['datetime'].append(entry.get('dt_txt'))
        time.sleep(0.2)

        # Append the city_data to the list
        all_cities_data.append(city_data)
    
    #LOAD
    try:
        print("host={} dbname={} user={} password={}".format(ENDPOINT, DB_NAME, USERNAME, PASSWORD))
        conn = psycopg2.connect("host={} dbname={} user={} password={}".format(ENDPOINT, DB_NAME, USERNAME, PASSWORD))

    except psycopg2.Error as e:
        print("Error: Could not make connection to the Postgres database")
        print(e)
    
    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print("Error: Could not get curser to the Database")
        print(e)

    # Auto commit is very important
    conn.set_session(autocommit=True)
    
    cur.execute("CREATE TABLE IF NOT EXISTS weather_tab (main_temps REAL, main_temp_min REAL, main_temp_max REAL, main_humidity INTEGER, weather_main TEXT, weather_description TEXT, clouds INTEGER, wind REAL, visibility INTEGER, precipitation REAL, rain REAL, snow REAL, datetime TEXT, city TEXT, lon REAL, lat REAL);")
    
    #cur.execute("TRUNCATE TABLE weather_tab;")
    
    try:
        for city_data in all_cities_data:
            data_to_insert = list(zip(
                city_data['main_temps'], city_data['main_temp_min'], city_data['main_temp_max'], city_data['main_humidity'],
                city_data['weather_main'], city_data['weather_description'], city_data['clouds'], city_data['wind'],
                city_data['visibility'], city_data['precipitation'], city_data['rain'], city_data['snow'], city_data['datetime'],
                [city_data['city']] * len(city_data['main_temps']),  # Repeat city name for all rows
                [city_data['lon']] * len(city_data['main_temps']),
                [city_data['lat']] * len(city_data['main_temps'])
            ))
    
            cur.executemany("""
                INSERT INTO weather_tab (
                    main_temps, main_temp_min, main_temp_max, main_humidity, weather_main, weather_description,
                    clouds, wind, visibility, precipitation, rain, snow, datetime,
                    city, lon, lat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, data_to_insert)
    except psycopg2.Error as e:
        print("Error: Inserting Rows")
        print(e)

        
    # Commit changes to the database
    conn.commit()
        
    try:
        cur.execute("SELECT * FROM weather_tab;")
    except psycopg2.Error as e:
        print("Error: select *")
        print (e)
    
    row = cur.fetchone()
    while row:
        print(row)
        row = cur.fetchone()

    cur.close()
    conn.close()
       
    return all_cities_data[0]
