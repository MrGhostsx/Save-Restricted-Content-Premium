import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

MONGO_URL = os.environ.get("MONGO_URL", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "1234569875"))

# Your Owner / Admin Id For Broadcast 
OWNER_ID = int(os.environ.get("OWNER_ID", "1234569875"))

# New: Channel & Group Requirements (Optional)
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "Tech_Shreyansh")  # e.g., "Tech_Shreyansh29"
GROUP_USERNAME = os.environ.get("GROUP_USERNAME", "Tech_Shreyansh2")      # e.g., "Tech_Shreyansh2"

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "MrGhostsx")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
