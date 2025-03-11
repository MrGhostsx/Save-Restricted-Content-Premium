# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2

from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from datetime import datetime, timedelta
import json
import os

# File to store approved users
APPROVED_USERS_FILE = "approved_users.json"

# Load approved users from file
def load_approved_users():
    if os.path.exists(APPROVED_USERS_FILE):
        try:
            with open(APPROVED_USERS_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, return an empty dictionary
            return {}
    return {}

# Save approved users to file
def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, 'w') as file:
        json.dump(approved_users, file, indent=4)

# Check if user is approved
def is_user_approved(user_id, approved_users):
    if str(user_id) in approved_users:
        expiry_date = datetime.strptime(approved_users[str(user_id)]['expiry'], '%Y-%m-%d %H:%M:%S')
        return datetime.now() < expiry_date
    return False

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

# Initialize the bot
bot = Bot()

# Command to approve a user
@bot.on_message(filters.command("approve") & filters.user(OWNER_ID))
async def approve_user(client, message):
    if len(message.command) < 3:
        await message.reply("Usage: /approve <user_id> <duration> (h for hours, d for days, m for months, q for quarterly)")
        return

    user_id = message.command[1]
    duration = message.command[2]

    try:
        if duration[-1] == 'h':
            hours = int(duration[:-1])
            expiry_date = datetime.now() + timedelta(hours=hours)
        elif duration[-1] == 'd':
            days = int(duration[:-1])
            expiry_date = datetime.now() + timedelta(days=days)
        elif duration[-1] == 'm':
            months = int(duration[:-1])
            expiry_date = datetime.now() + timedelta(days=months*30)
        elif duration[-1] == 'q':
            months = int(duration[:-1]) * 3
            expiry_date = datetime.now() + timedelta(days=months*30)
        else:
            await message.reply("Invalid duration format. Use h for hours, d for days, m for months, q for quarterly.")
            return
    except ValueError:
        await message.reply("Invalid duration value. Please provide a valid number.")
        return

    approved_users = load_approved_users()
    approved_users[user_id] = {'expiry': expiry_date.strftime('%Y-%m-%d %H:%M:%S')}
    save_approved_users(approved_users)

    await message.reply(f"User {user_id} approved until {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}.")

# Command to unapprove a user
@bot.on_message(filters.command("unapprove") & filters.user(OWNER_ID))
async def unapprove_user(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /unapprove <user_id>")
        return

    user_id = message.command[1]

    approved_users = load_approved_users()
    if user_id in approved_users:
        del approved_users[user_id]
        save_approved_users(approved_users)
        await message.reply(f"User {user_id} unapproved.")
    else:
        await message.reply(f"User {user_id} is not approved.")

# Command for users to check their plan details
@bot.on_message(filters.command("myplan"))
async def my_plan(client, message):
    user_id = str(message.from_user.id)
    approved_users = load_approved_users()

    if user_id in approved_users:
        expiry_date = datetime.strptime(approved_users[user_id]['expiry'], '%Y-%m-%d %H:%M:%S')
        time_left = expiry_date - datetime.now()

        if time_left.total_seconds() > 0:
            plan_details = (
                f"**Your Plan Details:**\n"
                f"👤 Username: `{message.from_user.username}`\n"
                f"🤖 Bot Name: `mrghostsx login`\n"
                f"⏳ Plan Expiry: `{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"⏰ Time Left: `{str(time_left).split('.')[0]}`"
            )
            await message.reply(plan_details)
        else:
            await message.reply("Your plan has expired. Contact admin To Buy Premium Subscription @SmartEdith_Bot")
    else:
        await message.reply("You do not have an active plan. Contact admin To Buy Premium Subscription @SmartEdith_Bot")

# Check if user is approved or is the owner before processing any message
@bot.on_message()
async def check_user_approval(client, message):
    approved_users = load_approved_users()
    user_id = str(message.from_user.id)

    # Allow owner to use the bot without approval
    if user_id == str(OWNER_ID):
        await message.continue_propagation()

    # Check if user is approved
    if is_user_approved(user_id, approved_users):
        await message.continue_propagation()
    else:
        await message.reply("You are not approved to use this bot. Contact admin To Buy Premium Subscription @SmartEdith_Bot")

# Run the bot
bot.run()
# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2
