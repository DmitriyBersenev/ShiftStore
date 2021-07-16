import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEETS_TOKEN = str(os.getenv('GOOGLE_SHEETS_TOKEN'))
