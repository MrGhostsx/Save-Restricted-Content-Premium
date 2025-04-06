from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URL, CHANNEL_USERNAME, GROUP_USERNAME
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import secrets
import string

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URL)
db = mongo_client['bot_database']
approved_users_collection = db['approved_users']
all_users_collection = db['all_users']
verified_users_collection = db['verified_users']  # To track who has joined channel/group
redeem_codes_collection = db['redeem_codes']  # To store redeem codes

# Load approved users from MongoDB and remove expired users
def load_approved_users():
    approved_users = {}
    for user in approved_users_collection.find():
        user_id = user['user_id']
        expiry = user['expiry']
        approved_users[user_id] = {'expiry': expiry}
    return remove_expired_users(approved_users)

# Save approved users to MongoDB
def save_approved_users(approved_users):
    approved_users_collection.delete_many({})
    for user_id, details in approved_users.items():
        approved_users_collection.insert_one({'user_id': user_id, 'expiry': details['expiry']})

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

# Load all users from MongoDB
def load_all_users():
    all_users = {}
    for user in all_users_collection.find():
        user_id = user['user_id']
        all_users[user_id] = True
    return all_users

# Save all users to MongoDB
def save_all_users(all_users):
    all_users_collection.delete_many({})
    for user_id in all_users:
        all_users_collection.insert_one({'user_id': user_id})

# Load verified users (who joined channel/group)
def load_verified_users():
    verified_users = {}
    for user in verified_users_collection.find():
        user_id = user['user_id']
        verified_users[user_id] = True
    return verified_users

# Save verified users
def save_verified_user(user_id):
    verified_users = load_verified_users()
    if str(user_id) not in verified_users:
        verified_users_collection.insert_one({'user_id': str(user_id)})

# Remove verified user if they leave channel/group
def remove_verified_user(user_id):
    verified_users_collection.delete_one({'user_id': str(user_id)})

# Update all users when a user interacts with the bot
def update_all_users(user_id):
    all_users = load_all_users()
    if str(user_id) not in all_users:
        all_users[str(user_id)] = True
        save_all_users(all_users)

# Check if user is approved
def is_user_approved(user_id, approved_users):
    if str(user_id) in approved_users:
        expiry_date = datetime.strptime(approved_users[str(user_id)]['expiry'], '%Y-%m-%d %H:%M:%S')
        return datetime.now() < expiry_date
    return False

# Check if user has joined channel and group
async def has_user_joined(client, user_id):
    try:
        # Check channel
        if CHANNEL_USERNAME:
            channel_member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
            if channel_member.status in ['left', 'kicked']:
                return False
        
        # Check group
        if GROUP_USERNAME:
            group_member = await client.get_chat_member(GROUP_USERNAME, user_id)
            if group_member.status in ['left', 'kicked']:
                return False
        
        return True
    except Exception as e:
        print(f"Error checking user membership: {e}")
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

# Create join buttons
def get_join_buttons():
    buttons = []
    if CHANNEL_USERNAME:
        buttons.append([InlineKeyboardButton("ⓘ Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")])
    if GROUP_USERNAME:
        buttons.append([InlineKeyboardButton("♡ ̆̈ Join Group", url=f"https://t.me/{GROUP_USERNAME}")])
    buttons.append([InlineKeyboardButton("☘️ I've Joined", callback_data="check_joined")])
    return InlineKeyboardMarkup(buttons)

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
                f"👤 Username: {message.from_user.username}\n"
                f"🤖 Bot Name: @SmartEdith_Bot\n"
                f"⏳ Plan Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏰ Time Left: {str(time_left).split('.')[0]}"
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
        response += f"👤 User ID: {user_id}\n"
        response += f"⏳ Expiry Date: {expiry_date}\n"
        response += f"⏰ Remaining Days: {remaining_days}\n\n"

    response += f"\n**Total Approved Users:** {len(approved_users)}"
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
        f"☘️ Success: {success_count}\n"
        f"❌ Failed: {fail_count}"
    )

# Command to generate redeem codes (admin only)
@bot.on_message(filters.command("generateredeem") & filters.user(OWNER_ID))
async def generate_redeem_code(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /generateredeem <count>")
        return

    try:
        count = int(message.command[1])
        if count <= 0:
            await message.reply("Count must be a positive integer.")
            return
    except ValueError:
        await message.reply("Invalid count. Please provide a valid number.")
        return

    # Generate random redeem codes
    alphabet = string.ascii_uppercase + string.digits
    redeem_codes = []

    for _ in range(count):
        code = ''.join(secrets.choice(alphabet) for _ in range(10))
        redeem_codes.append(code)
        redeem_codes_collection.insert_one({
            'code': code,
            'used': False,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    await message.reply(f"Generated {count} redeem codes:\n\n" + "\n".join(redeem_codes))

# Command to list all redeem codes (admin only)
@bot.on_message(filters.command("listredeem") & filters.user(OWNER_ID))
async def list_redeem_codes(client, message):
    unused_codes = list(redeem_codes_collection.find({'used': False}))
    
    if not unused_codes:
        await message.reply("No unused redeem codes available.")
        return

    response = "**Unused Redeem Codes:**\n\n"
    for code in unused_codes:
        response += f"🔑 Code: `{code['code']}`\n"
        response += f"🕒 Generated At: {code['generated_at']}\n\n"

    await message.reply(response)

# Command for users to redeem codes
@bot.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    user_id = str(message.from_user.id)

    if len(message.command) < 2:
        await message.reply("Usage: /redeem code")
        return

    code = message.command[1]

    # Check if the code exists and is not used
    redeem_code_data = redeem_codes_collection.find_one({'code': code, 'used_by': None})

    if not redeem_code_data:
        await message.reply("❌ Invalid or already used redeem code.")
        return

    # Mark the code as used by the user and delete it from MongoDB
    redeem_codes_collection.delete_one({'code': code})

    # Add the user to the approved users list with a 30-minute expiry
    expiry_date = datetime.now() + timedelta(minutes=30)
    approved_users = load_approved_users()
    approved_users[user_id] = {'expiry': expiry_date.strftime('%Y-%m-%d %H:%M:%S')}
    save_approved_users(approved_users)

    await message.reply(f"✅ Redeem code `{code}` successfully applied! You can use the bot for 30 minutes.")

# Callback query handler for join verification
@bot.on_callback_query(filters.regex("^check_joined$"))
async def check_joined_callback(client, callback_query):
    user_id = callback_query.from_user.id
    
    has_joined = await has_user_joined(client, user_id)
    
    if has_joined:
        save_verified_user(user_id)
        await callback_query.answer("🍀 Verification successful! You can now use the bot.", show_alert=True)
        await callback_query.message.delete()
    else:
        await callback_query.answer("⚠️ Please join both channel and group first!", show_alert=True)

# Check if user is approved or is the owner before processing any message
@bot.on_message()
async def check_user_approval(client, message):
    user_id = str(message.from_user.id)

    # Update all users list
    update_all_users(user_id)

    approved_users = load_approved_users()
    verified_users = load_verified_users()

    # Allow owner to use the bot without approval
    if user_id == str(OWNER_ID):
        await message.continue_propagation()

    # Check if user needs to join channel/group
    if CHANNEL_USERNAME or GROUP_USERNAME:
        # First check if they're in verified users
        if user_id not in verified_users:
            join_message = "**⚠️ Access Restricted!**\n\n"
            join_message += "To use this bot, you must join our "
            
            if CHANNEL_USERNAME and GROUP_USERNAME:
                join_message += "channel and group first."
            elif CHANNEL_USERNAME:
                join_message += "channel first."
            else:
                join_message += "group first."
                
            join_message += "\n\nAfter joining, click the button below to verify."
            
            await message.reply(
                join_message,
                reply_markup=get_join_buttons(),
                disable_web_page_preview=True
            )
            return
        else:
            # If they're in verified users, check if they're still members
            has_joined = await has_user_joined(client, int(user_id))
            if not has_joined:
                remove_verified_user(user_id)
                join_message = "**⚠️ Access Restricted!**\n\n"
                join_message += "You left our channel/group. Please rejoin to continue using the bot."
                
                await message.reply(
                    join_message,
                    reply_markup=get_join_buttons(),
                    disable_web_page_preview=True
                )
                return

    # Allow approved users to use all commands except /broadcast, /approve, and /unapprove
    if is_user_approved(user_id, approved_users):
        if message.command and message.command[0] in ["broadcast", "approve", "unapprove", "generateredeem", "listredeem"]:
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
