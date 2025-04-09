#  config.py

from dotenv import load_dotenv
import os

# Load .env file explicitly
load_dotenv(dotenv_path="config.env")

# Telegram API credentials
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB connection string
MONGO_URL = os.getenv("MONGO_URL")

# Telegram group chat ID used for logging purposes
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

# Convert comma-separated string into list of integers
BOT_ADMINS = list(map(int, os.getenv("BOT_ADMINS", "").split(",")))

