import requests
import os

def tourism_loader():
    api_key = os.getenv("TOURISM_API_KEY")

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
        destinations = [item["name"] for item in data["data"]]
        print(type(destinations))
        print(destinations)
        
    else:
        print("Failed to retrieve data from the API")

    return(destinations)