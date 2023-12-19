import requests

def fetch_and_transform_data(api_key, api_url):
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    destination_list = []

    for page in range(20): #sometimes if fails due to the large number here, might try smaller (e.g. 5), or just rerun
        url = f"{api_url}&page={page}"
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

    return destination_list

api_key = 'HFjqHMLW8y8HdSOUjKBfL9JZYPQo5Rvo3Qq1yk3z'
API_URL_DEST = 'https://opendata.myswitzerland.io/v1/destinations/?hitsPerPage=50&striphtml=true'
data_dest = fetch_and_transform_data(api_key, API_URL_DEST)

print(data_dest[0]) #to test how the destination looks 