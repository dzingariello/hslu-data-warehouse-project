import requests
import json

def loader():
    api_key = '_'

    url = "https://opendata.myswitzerland.io/v1/destinations"

    # Define the headers
    headers = {
        "accept": "application/json",
        "x-api-key": f"{api_key}"
    }

    # Make the GET request with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Get all destination titles from the response data
        titles = [item["name"] for item in data["data"]]
        
        print(titles)
        
    else:
        print("Failed to retrieve data from the API")