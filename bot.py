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

# File to store all users
ALL_USERS_FILE = "all_users.json"

# Load approved users from file and remove expired users
def load_approved_users():
    if os.path.exists(APPROVED_USERS_FILE):
        try:
            with open(APPROVED_USERS_FILE, 'r') as file:
                approved_users = json.load(file)
                # Remove expired users
                approved_users = remove_expired_users(approved_users)
                return approved_users
        except json.JSONDecodeError:
            return {}
    return {}

# Save approved users to file
def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, 'w') as file:
        json.dump(approved_users, file, indent=4)

# Remove expired users from the approved users list
def remove_expired_users(approved_users):
    current_time = datetime.now()
    expired_users = []

    for user_id, details in approved_users.items():
        expiry_date = datetime.strptime(details['expiry'], '%Y-%m-%d %H:%M:%S')
        if current_time > expiry_date:
            expired_users.append(user_id)

    for user_id in expired_users:
        del approved_users[user_id]

    if expired_users:
        save_approved_users(approved_users)

    return approved_users

# Load all users from file
def load_all_users():
    if os.path.exists(ALL_USERS_FILE):
        try:
            with open(ALL_USERS_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

# Save all users to file
def save_all_users(all_users):
    with open(ALL_USERS_FILE, 'w') as file:
        json.dump(all_users, file, indent=4)

# Update all users when a user interacts with the bot
def update_all_users(user_id):
    all_users = load_all_users()
    if str(user_id) not in all_users:
        all_users[str(user_id)] = True  # Store the user ID
        save_all_users(all_users)

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
                f"🤖 Bot Name: `@SmartEdith_Bot`\n"
                f"⏳ Plan Expiry: `{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"⏰ Time Left: `{str(time_left).split('.')[0]}`"
            )
            await message.reply(plan_details)
        else:
            await message.reply("Your plan has expired. Contact admin To Buy Premium Subscription @SmartEdith_Bot")
    else:
        await message.reply("You do not have an active plan. Contact admin To Buy Premium Subscription @SmartEdith_Bot")

# Command to list all approved users (owner/admin only)
@bot.on_message(filters.command("approvedusers") & filters.user(OWNER_ID))
async def list_approved_users(client, message):
    approved_users = load_approved_users()

    if not approved_users:
        await message.reply("No users are currently approved.")
        return

    response = "**Approved Users:**\n\n"
    for user_id, details in approved_users.items():
        expiry_date = details['expiry']
        remaining_days = (datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S') - datetime.now()).days
        response += f"👤 User ID: `{user_id}`\n"
        response += f"⏳ Expiry Date: `{expiry_date}`\n"
        response += f"⏰ Remaining Days: `{remaining_days}`\n\n"

    response += f"\n**Total Approved Users:** `{len(approved_users)}`"
    await message.reply(response)

# Command to display plan information
@bot.on_message(filters.command("planinfo"))
async def plan_info(client, message):
    plan_table = (
        "**📊 Subscription Plans:**\n\n"
        "```"
        "+--------------+------------+\n"
        "|  Duration    | Price (INR)|\n"
        "+--------------+------------+\n"
        "| 1 Day        | ₹20        |\n"
        "| 1 Week       | ₹80        |\n"
        "| 1 Month      | ₹250       |\n"
        "| 3 Months     | ₹700       |\n"
        "| 6 Months     | ₹1200      |\n"
        "| 1 Year       | ₹2500      |\n"
        "+--------------+------------+```\n\n"
        "Contact admin to buy a plan: @Tech_Shreyansh29"
    )
    await message.reply(plan_table)

# Broadcast command (admin only)
@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /broadcast <message>")
        return

    broadcast_message = " ".join(message.command[1:])
    all_users = load_all_users()

    if not all_users:
        await message.reply("No users to broadcast to.")
        return

    await message.reply(f"Broadcasting message to {len(all_users)} users...")

    success_count = 0
    fail_count = 0

    for user_id in all_users:
        try:
            await client.send_message(int(user_id), broadcast_message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
            fail_count += 1

    await message.reply(
        f"Broadcast completed!\n"
        f"✅ Success: {success_count}\n"
        f"❌ Failed: {fail_count}"
    )

# Check if user is approved or is the owner before processing any message
@bot.on_message()
async def check_user_approval(client, message):
    user_id = str(message.from_user.id)

    # Update all users list
    update_all_users(user_id)

    approved_users = load_approved_users()

    # Allow owner to use the bot without approval
    if user_id == str(OWNER_ID):
        await message.continue_propagation()

    # Allow approved users to use all commands except /broadcast, /approve, and /unapprove
    if is_user_approved(user_id, approved_users):
        if message.command and message.command[0] in ["broadcast", "approve", "unapprove"]:
            await message.reply("This command is restricted to the owner only.")
        else:
            await message.continue_propagation()
    else:
        await message.reply("You are not approved to use this bot. Contact admin To Buy Premium Subscription @SmartEdith_Bot")

# Run the bot
bot.run()


# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2
