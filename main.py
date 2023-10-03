from dotenv import load_dotenv
from src.tourism_loader import tourism_loader
from src.youtube_loader import youtube_loader

def load_api_keys():
    load_dotenv()

def main():
    load_api_keys()
    tourism_loader()

if __name__ == "__main__":
    main()