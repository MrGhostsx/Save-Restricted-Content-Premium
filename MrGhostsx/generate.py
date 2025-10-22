# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return await message.reply("**You are not logged in!**")
    # Use remove_session instead of set_session with None
    await db.remove_session(message.from_user.id)
    await message.reply("**Logout Successfully** 👻")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Your Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return 
    
    user_id = int(message.from_user.id)
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    
    try:
        await client.connect()
    except Exception as e:
        return await message.reply(f"<b>Connection Error:</b> `{e}`")
    
    await phone_number_msg.reply("Sending OTP...")
    
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel The Process**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
        await client.disconnect()
        return
    except Exception as e:
        await phone_number_msg.reply(f'**Error sending OTP:** `{e}`')
        await client.disconnect()
        return
    
    if phone_code_msg.text == '/cancel':
        await client.disconnect()
        return await phone_code_msg.reply('<b>Process cancelled!</b>')
    
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        await client.disconnect()
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        await client.disconnect()
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Your account has enabled two-step verification. Please provide the password.\n\nEnter /cancel to cancel The Process**', filters=filters.text, timeout=300)
        if two_step_msg.text == '/cancel':
            await client.disconnect()
            return await two_step_msg.reply('<b>Process cancelled!</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**')
            await client.disconnect()
            return
    
    try:
        string_session = await client.export_session_string()
        await client.disconnect()
        
        if len(string_session) < SESSION_STRING_SIZE:
            return await message.reply('<b>Invalid session string</b>')
        
        # Check if user exists in database, if not add them
        if not await db.is_user_exist(message.from_user.id):
            user_name = message.from_user.first_name or "User"
            await db.add_user(message.from_user.id, user_name)
        
        # Save session to database
        await db.set_session(message.from_user.id, string_session)
        
        # Verify session by creating a client and getting user info
        async with Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH) as uclient:
            user_info = await uclient.get_me()
            await bot.send_message(
                message.from_user.id, 
                f"<b>✅ Account Login Successfully!</b>\n\n"
                f"<b>Name:</b> {user_info.first_name}\n"
                f"<b>Username:</b> @{user_info.username or 'N/A'}\n"
                f"<b>User ID:</b> <code>{user_info.id}</code>\n\n"
                f"<i>If You Get Any Error Related To AUTH KEY Then /logout first and /login again</i>"
            )
            
    except Exception as e:
        await client.disconnect()
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")

# Don't Remove Credit Tg - @Tech_Shreyansh29
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@techshreyansh
# Ask Doubt on telegram @Tech_Shreyansh2
