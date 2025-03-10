# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        super().__init__(
            "mrghostsx login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="MrGhostsx"),
            workers=50,
            sleep_threshold=10
        )

      
    async def start(self):
            
        await super().start()
        print('Bot Started Powered By @Tech_Shreyansh29')

    async def stop(self, *args):

        await super().stop()
        print('Bot Stopped Bye')

Bot().run()

# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2
