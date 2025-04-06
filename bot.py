# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URL, CHANNEL_USERNAME, GROUP_USERNAME
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import secrets
import string

# MongoDB Setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client['bot_database']
approved_users = db['approved_users']
all_users = db['all_users']
verified_users = db['verified_users']  # Stores users who joined channel/group
redeem_codes = db['redeem_codes']

# Load approved users (remove expired)
def load_approved_users():
    current_time = datetime.now()
    active_users = {}
    for user in approved_users.find():
        expiry = datetime.strptime(user['expiry'], '%Y-%m-%d %H:%M:%S')
        if current_time < expiry:
            active_users[user['user_id'] = {'expiry': user['expiry']}
        else:
            approved_users.delete_one({'user_id': user['user_id']})
    return active_users

# Verify user joined channel/group
async def check_membership(client, user_id):
    try:
        if CHANNEL_USERNAME:
            member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ['left', 'kicked']:
                return False
        if GROUP_USERNAME:
            member = await client.get_chat_member(GROUP_USERNAME, user_id)
            if member.status in ['left', 'kicked']:
                return False
        return True
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# Join Buttons
def join_buttons():
    buttons = []
    if CHANNEL_USERNAME:
        buttons.append([InlineKeyboardButton("👻 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")])
    if GROUP_USERNAME:
        buttons.append([InlineKeyboardButton("👻 Join Channel", url=f"https://t.me/{GROUP_USERNAME}")])
    buttons.append([InlineKeyboardButton("☘️ Check Again", callback_data="verify_joined")])
    return InlineKeyboardMarkup(buttons)

# Bot Class
class Bot(Client):
    def __init__(self):
        super().__init__(
            "mrghostsx_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins")
        )

    async def start(self):
        await super().start()
        print("Bot Started! Powered by @Tech_Shreyansh29")

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped!")

bot = Bot()

# Callback: Verify User Joined
@bot.on_callback_query(filters.regex("^verify_joined$"))
async def verify_joined(client, callback):
    user_id = callback.from_user.id
    if await check_membership(client, user_id):
        verified_users.insert_one({'user_id': user_id})
        await callback.answer("✅ Verified! Now you can use the bot.", show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("❌ Join both channel & group first!", show_alert=True)

# Message Handler: Force Join Check
@bot.on_message(filters.private & ~filters.user(OWNER_ID))
async def force_join_check(client, message):
    user_id = message.from_user.id
    if not verified_users.find_one({'user_id': user_id}):
        await message.reply(
            "**⚠️ Access Denied!**\nJoin our channel & group to use me:",
            reply_markup=join_buttons()
        )
    elif not await check_membership(client, user_id):
        verified_users.delete_one({'user_id': user_id})
        await message.reply(
            "**🚫 Removed Access!**\nYou left our channel/group. Rejoin to continue:",
            reply_markup=join_buttons()
        )
    else:
        await message.continue_propagation()

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

    await message.reply(f"User `{user_id}` approved until `{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}`.")

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
        await message.reply(f"User `{user_id}` unapproved.")
    else:
        await message.reply(f"User `{user_id}` is not approved.")

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
        response += f"👤 User ID: `{user_id}`\n"  # Click-to-copy user ID
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

# Command to display terms and conditions
@bot.on_message(filters.command("terms"))
async def terms_and_conditions(client, message):
    terms = (
        "> 📜 **Terms and Conditions** 📜\n\n"
        "✨ We are not responsible for user deeds, and we do not promote copyrighted content. If any user engages in such activities, it is solely their responsibility.\n"
        "✨ Upon purchase, we do not guarantee the uptime, downtime, or the validity of the plan. __Authorization and banning of users are at our discretion; we reserve the right to ban or authorize users at any time.__\n"
        "✨ Payment to us **__does not guarantee__** authorization for the batch command. All decisions regarding authorization are made at our discretion and mood.\n"
    )
    await message.reply(terms)

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

    await message.reply(f"Broadcasting message to `{len(all_users)}` users...")

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
        f"✅ Success: `{success_count}`\n"
        f"❌ Failed: `{fail_count}`"
    )

# Command to generate multiple redeem codes (admin only)
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

    # Generate multiple redeem codes
    alphabet = string.ascii_letters + string.digits
    redeem_codes = []

    for _ in range(count):
        redeem_code = ''.join(secrets.choice(alphabet) for i in range(10))
        redeem_codes.append(redeem_code)
        redeem_codes_collection.insert_one({
            'code': redeem_code,
            'used_by': None,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    await message.reply(f"Generated `{count}` redeem codes:\n\n" + "\n".join([f"`{code}`" for code in redeem_codes]))

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

# Command to list all redeem codes (admin only)
@bot.on_message(filters.command("listredeem") & filters.user(OWNER_ID))
async def list_redeem_codes(client, message):
    # Find only unused redeem codes
    redeem_codes = redeem_codes_collection.find({'used_by': None})

    if not redeem_codes:
        await message.reply("No unused redeem codes available.")
        return

    response = "**Unused Redeem Codes:**\n\n"
    for code in redeem_codes:
        response += f"🔑 Code: `{code['code']}`\n"  # Click-to-copy redeem code
        response += f"🕒 Generated At: `{code['generated_at']}`\n\n"

    await message.reply(response)

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
        if message.command and message.command[0] in ["broadcast", "approve", "unapprove", "generateredeem"]:
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
