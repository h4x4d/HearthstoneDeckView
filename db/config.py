import os

from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN")

GROUP_ID = os.getenv("GROUP_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

FOLDER = "cards/"
