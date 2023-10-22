from dotenv import load_dotenv
from src.tourism_loader import tourism_loader
from src.youtube_loader import youtube_loader
from src.db_connect import db_connect

def load_env():
    load_dotenv()

def main():
    load_env()
    # destinations = tourism_loader()
    # print("==========================")
    # print(destinations)
    # db_connect(destinations)

    youtube_loader()

if __name__ == "__main__":
    main()