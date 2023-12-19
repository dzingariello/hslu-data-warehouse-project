import requests
import os

def youtube_loader():
    api_key = os.getenv("YOUTUBE_API_KEY")

    # This is the Channel ID for the @MySwitzerland Account
    channel_id = 'UCggBc5kNSAH4kFKkrYBzddQ'

    # Make a request to the YouTube Data API to fetch video details
    url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet&order=date&maxResults=100'

    response = requests.get(url)

   
    if response.status_code == 200:
        data = response.json()
        # Extract video names from the response
        video_names = [item['snippet']['title'] for item in data['items']]
        # Print the video names
        for name in video_names:
            print(name)
    else:
        print(f"API request failed with status code: {response.status_code}")
        print(response.text)
