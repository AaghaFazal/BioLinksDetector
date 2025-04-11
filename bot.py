from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter, ParseMode
from pyrogram.types import Message, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import PeerIdInvalid, FloodWait
from pymongo import MongoClient
import speedtest
import asyncio
import logging
import psutil
import time
import re
import config 


import os
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs.txt", encoding="utf-8"),
        logging.StreamHandler()  # Optional: also show in terminal
    ]
)


bot = Client("LinkDetector", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

# Connect to MongoDB
mongo_client = MongoClient(config.MONGO_URL)
db = mongo_client["LinkDetector"]
nobiolink_collection = db["Groups"]
admin_collection = db["GroupsAdmins"]
whitelisted_users_collection = db["WhitelistedUsers"]
bonus_collection = db["BonusUsers"]
users_collection = db["Users"]
chats_collection = db["Chats"]
cooldown_collection = db["Cooldowns"]  
bio_cooldown_collection = db["BioCooldowns"]
logs_control_collection = db["LogsControl"]

start_time = time.time()


@bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user = message.from_user
    user_id = user.id
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    username = user.username or "No username"
    # await message.delete()

    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

        # Check if logging is enabled
        log_settings = logs_control_collection.find_one({"_id": "logs"})
        if log_settings and log_settings.get("enabled", False):
            log_text = (
                f"🆕 **New User Started Bot**\n"
                f"👤 Name: {full_name}\n" 
                f"🔗 Username: @{username if username != 'No username' else 'N/A'}\n"
                f"🆔 User ID: `{user_id}`"
            )
            try:
                await client.send_message(int(config.LOG_GROUP_ID), log_text)
            except PeerIdInvalid:
                logging.error(f"❌ Failed to log to group {config.LOG_GROUP_ID}. Make sure the bot is added and has permission.")

    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        # [InlineKeyboardButton("💬 Group", url="https://t.me/TheTeamXSupport"),
        #  InlineKeyboardButton("📡 Channel", url="https://t.me/TheTeamXUpdate")],
        # [InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/AaghaFazal"),
        #  InlineKeyboardButton("👑 Owner", url="https://t.me/LALALORRY")],
        [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{bot.me.username}?startgroup=true")]
    ])

    user_mention = user.mention
    welcome_text = (
        f"Hello {user_mention},\n\n"
        "Welcome To\n"
        "**Bio Link Detector**\n"
        "Your automated solution for maintaining a secure and organized group environment.\n\n"
        "> 🔍 **What I Do:**\n"
        "> • Detect and flag links in user bios.\n"
        "> • Automatically delete messages from users with unauthorized links in their bios.\n"
        "> • Provide admins with full control to enable or disable bio link detection.\n"
        "> • Allow whitelisting of trusted users for seamless participation.\n\n"
        "⚙️ **Controls:**\n"
        "• `/privacy` – Display privacy policy.\n"
        "• `/biolink` – Enable or disable bio link detection.\n"
        "• `/refresh` – Re-fetches admin list and updates database.\n"
        "• `/whitelist` – Whitelist a user (reply or use username).\n"
        "• `/delist` – Remove a user from the whitelist.\n"
        "• `/list` – Show all whitelisted users.\n\n"
        "> Integrate me into your group to ensure a **spam-free and well-moderated** experience. 🚀\n\n"
        "> **Make sure to grant me admin permissions** with `Delete Messages` enabled for optimal functionality."
    )

    await message.reply_text(welcome_text, reply_markup=keyboard)

    if not bonus_collection.find_one({"user_id": user_id}):
        bonus_collection.insert_one({"user_id": user_id, "message_count": 0})
        await asyncio.sleep(2)
        await message.reply_text("> 🎉Congratulations! You are now permitted to send **two messages** without restrictions in any group where I serve as a moderator.")


@bot.on_message(filters.command("start") & filters.group)
async def start_in_group(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the group is already in the database
    group_exists = chats_collection.find_one({"chat_id": chat_id})

    if not group_exists:
        chats_collection.insert_one({"chat_id": chat_id})

    keyboard = InlineKeyboardMarkup([
        # [InlineKeyboardButton("💬 Group", url="https://t.me/TheTeamXSupport"),
        #  InlineKeyboardButton("📡 Channel", url="https://t.me/TheTeamXUpdate")],
        # [InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/AaghaFazal"),
        #  InlineKeyboardButton("👑 Owner", url="https://t.me/LALALORRY")],
        [InlineKeyboardButton("See Magic✨", url=f"https://t.me/{bot.me.username}?start=true")]
    ])

    welcome_message = (
        "Welcome To\n"
        "**Bio Link Detector**\n"
        "Your automated solution for maintaining a secure and organized group environment.\n\n"
        "> 🔍 **What I Do:**\n"
        "> • Detect and flag links in user bios.\n"
        "> • Automatically delete messages from users with unauthorized links in their bios.\n"
        "> • Provide admins with full control to enable or disable bio link detection.\n"
        "> • Allow whitelisting of trusted users for seamless participation.\n\n"
        "⚙️ **Controls:**\n"
        "• `/privacy` – Display privacy policy.\n"
        "• `/biolink` – Enable or disable bio link detection.\n"
        "• `/refresh` – Re-fetches admin list and updates database.\n"
        "• `/whitelist` – Whitelist a user (reply or use username).\n"
        "• `/delist` – Remove a user from the whitelist.\n"
        "• `/list` – Show all whitelisted users.\n"
        "• `/stats` – Show bot performance and resource usage.\n\n"
        "> **Make sure to grant me admin permissions** with `Delete Messages` enabled for optimal functionality.\n\n"
        "> 🚀 Configure me now to ensure a **spam-free and well-moderated** experience!"
    )

    # Always send the welcome message
    await message.reply_text(welcome_message, reply_markup=keyboard)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.on_message(filters.command("privacy"))
async def send_privacy_button(client: Client, message: Message):
    """Send an inline button and image for the privacy policy"""

    await message.delete()

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔒 Click here to see Privacy", url="https://biolinksdetector.github.io/Bot")]]
    )

    privacy_caption = """🔒 **Privacy Policy** 🔒
Your privacy is important to us. To learn more about how we collect, use, and protect your data, please review our [Privacy Policy](https://biolinksdetector.github.io/Bot).

If you have any questions or concerns, feel free to reach out to our [support team](https://t.me/TheTeamXSupport).
"""

    await client.send_photo(
        chat_id=message.chat.id,
        photo="https://biolinksdetector.github.io/Bot/src/privacy_n_policy.jpg",
        caption=privacy_caption,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def get_admins_from_db(chat_id):
    """Retrieve admin list from MongoDB"""
    data = admin_collection.find_one({"chat_id": chat_id})
    return data["admins"] if data else []

async def update_admins_in_db(chat_id, admins):
    """Update the admin list for a specific group in MongoDB"""
    admin_collection.update_one(
        {"chat_id": chat_id}, 
        {"$set": {"admins": admins}}, 
        upsert=True
    )

async def is_admins(chat_id):
    """Fetch admin list from DB or update if empty"""
    admins = await get_admins_from_db(chat_id)

    if not admins:  # If no admins are cached, fetch from Telegram
        admins = []
        async for member in bot.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            admins.append(member.user.id)
        await update_admins_in_db(chat_id, admins)  # Save in MongoDB

    return admins

async def is_on_cooldown(chat_id):
    """Check if the chat is on cooldown."""
    data = cooldown_collection.find_one({"chat_id": chat_id})
    if data:
        last_used = data["last_used"]
        if time.time() - last_used < 60:  # 60 seconds cooldown
            return True
    return False

async def set_cooldown(chat_id):
    """Set cooldown timestamp for the chat."""
    cooldown_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"last_used": time.time()}},
        upsert=True
    )

async def get_cooldown_remaining(chat_id):
    """Return the number of seconds remaining on cooldown, or 0 if not on cooldown."""
    data = cooldown_collection.find_one({"chat_id": chat_id})
    if data:
        last_used = data["last_used"]
        elapsed = time.time() - last_used
        remaining = 60 - elapsed
        return max(0, int(remaining))
    return 0


@bot.on_message(filters.command("refresh") & filters.group)
async def refresh_admins(client: Client, message: Message):
    """Re-fetch admin list for the current group and update MongoDB"""
    chat_id = message.chat.id

    # Check cooldown
    cooldown_remaining = await get_cooldown_remaining(chat_id)
    if cooldown_remaining > 0:
        await message.delete()
        cooldown_message = await bot.send_message(
            chat_id, 
            f"⏳ Please wait **{cooldown_remaining} second{'s' if cooldown_remaining != 1 else ''}** before refreshing again!"
        )
        await asyncio.sleep(5)
        await cooldown_message.delete()
        return

    # Re-fetch from Telegram and update MongoDB
    updated_admins = []
    async for member in bot.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        updated_admins.append(member.user.id)

    await update_admins_in_db(chat_id, updated_admins)
    await set_cooldown(chat_id)
    await message.delete()

    response = await client.send_message(
        chat_id,
        f"> ✅ The admin list has been refreshed.\nTotal Admins: **{len(updated_admins)}**"
    )
    await asyncio.sleep(10)
    await response.delete()

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.on_message(filters.command("biolink") & filters.group)
async def nobiolink_toggle(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if message.from_user exists (to handle anonymous admins)
    if not message.from_user:
        await message.delete()
        anonymous_warning_msg = await client.send_message(chat_id, "⚠️ This command can't be used by anonymous admins.")
        await asyncio.sleep(10)
        await anonymous_warning_msg.delete()
        return

    user_id = message.from_user.id

    admins = await is_admins(chat_id)
    if user_id not in admins:
        warning_message = f"[{message.from_user.first_name}](tg://user?id={user_id})\n⚠️ Only **admins** can enable or disable Bio Link Detection mode!"
        sent_warning_message = await client.send_message(chat_id, warning_message)
        await message.delete()
        await asyncio.sleep(11)
        await sent_warning_message.delete()
        return

    await message.delete()

    # Add group to broadcast list if not already present
    if not chats_collection.find_one({"chat_id": chat_id}):
        chats_collection.insert_one({"chat_id": chat_id})

    if nobiolink_collection.find_one({"chat_id": chat_id}):
        nobiolink_collection.delete_one({"chat_id": chat_id})
        response = "🚫 Bio Link Detection \n**disabled**."
    else:
        nobiolink_collection.insert_one({"chat_id": chat_id})
        response = "✅ Bio Link Detection \n**enabled**\n\n\nUsers with links in their **bio** will have their messages deleted."

    response_message = f"[{message.from_user.first_name}](tg://user?id={user_id}), \n{response}"
    sent_response_message = await client.send_message(chat_id, response_message)
    await asyncio.sleep(11)
    await sent_response_message.delete()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Approves a user to bypass bio link detection. Only admins can execute this command.
@bot.on_message(filters.command("whitelist") & filters.group)
async def approve_user(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = None

    # Check if message.from_user exists (to handle anonymous admins)
    if not message.from_user:
        await message.delete()
        anonymous_warning_msg = await client.send_message(chat_id, "⚠️ This command can't be used by anonymous admins.")
        await asyncio.sleep(10)
        await anonymous_warning_msg.delete()
        return
    
    admins = await is_admins(chat_id)
    if message.from_user.id not in admins:
        warning_message = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})\n⚠️ Only **admins** can whitelist users!"
        sent_warning_message = await client.send_message(chat_id, warning_message)
        await message.delete()
        await asyncio.sleep(11)
        await sent_warning_message.delete()
        return
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        username = message.command[1].lstrip('@')
        try:
            user = await bot.get_users(username)
            user_id = user.id
        except Exception as e:
            logging.error(f"Error fetching user: {e}")
            error_message = await client.send_message(chat_id, "Invalid username or user not found.")
            await message.delete()
            await asyncio.sleep(10)
            await error_message.delete()
            return
    else:
        prompt_message = await client.send_message(chat_id, "Please reply to a message or mention a username to whitelist.")
        await message.delete()
        await asyncio.sleep(10)
        await prompt_message.delete()
        return
    
    # Insert only if user is not already in the whitelisted list
    if whitelisted_users_collection.count_documents({"chat_id": chat_id, "user_id": user_id}, limit=1) == 0:
        whitelisted_users_collection.insert_one({"chat_id": chat_id, "user_id": user_id})
    
    response = f"> ✅ [{user_id}](tg://user?id={user_id}) has been whitelisted."
    sent_response_message = await client.send_message(chat_id, response)
    await asyncio.sleep(11)
    await sent_response_message.delete()
    await message.delete()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Delist a user from the whitelisted list. Only admins can execute this command.
@bot.on_message(filters.command("delist") & filters.group)
async def delist_whitelisted_user(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = None

    # Check if message.from_user exists (to handle anonymous admins)
    if not message.from_user:
        await message.delete()
        anonymous_warning_msg = await client.send_message(chat_id, "⚠️ This command can't be used by anonymous admins.")
        await asyncio.sleep(10)
        await anonymous_warning_msg.delete()
        return
    
    admins = await is_admins(chat_id)
    if message.from_user.id not in admins:
        warning_message = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})\n⚠️ Only **admins** can delist whitelisted users!"
        sent_warning_message = await client.send_message(chat_id, warning_message)
        await message.delete()
        await asyncio.sleep(11)
        await sent_warning_message.delete()
        return
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        username = message.command[1].lstrip('@')
        try:
            user = await bot.get_users(username)
            user_id = user.id
        except Exception as e:
            logging.error(f"Error fetching user: {e}")
            error_message = await client.send_message(chat_id, "Invalid username or user not found.")
            await message.delete()
            await asyncio.sleep(10)
            await error_message.delete()
            return
    else:
        prompt_message = await client.send_message(chat_id, "Please reply to a message or mention a username to delist.")
        await message.delete()
        await asyncio.sleep(10)
        await prompt_message.delete()
        return
    
    # Check and delist user from the database
    if whitelisted_users_collection.delete_one({"chat_id": chat_id, "user_id": user_id}).deleted_count > 0:
        response = f"🚫 [{user_id}](tg://user?id={user_id}) has been delisted from the whitelisted list."
    else:
        response = "ℹ️ This user is not in the whitelisted list."
    
    sent_response_message = await client.send_message(chat_id, response)
    await asyncio.sleep(11)
    await sent_response_message.delete()
    await message.delete()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Lists all whitelisted users in the group chat. Only admins can execute this command.
@bot.on_message(filters.command("list") & filters.group)
async def list_whitelisted_users(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if message.from_user exists (to handle anonymous admins)
    if not message.from_user:
        await message.delete()
        anonymous_warning_msg = await client.send_message(chat_id, "⚠️ This command can't be used by anonymous admins.")
        await asyncio.sleep(10)
        await anonymous_warning_msg.delete()
        return

    admins = await is_admins(chat_id)
    if message.from_user.id not in admins:
        warning_message = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})\n⚠️ Only **admins** can view the list of whitelisted users!"
        sent_warning_message = await client.send_message(chat_id, warning_message)
        await message.delete()
        await asyncio.sleep(11)
        await sent_warning_message.delete()
        return

    whitelisted_users = list(whitelisted_users_collection.find({"chat_id": chat_id}))

    if not whitelisted_users:
        no_users_msg = await client.send_message(chat_id, "ℹ️ No users have been whitelisted yet.")
        await message.delete()
        await asyncio.sleep(10)
        await no_users_msg.delete()
        return

    user_list = "> **Whitelisted Users:**\n\n"
    for user in whitelisted_users:
        try:
            user_info = await client.get_users(user['user_id'])
            full_name = user_info.first_name
            if user_info.last_name:
                full_name += f" {user_info.last_name}"
            user_list += f"- [{full_name}](tg://user?id={user['user_id']})\n"
        except Exception as e:
            logging.error(f"Error fetching user info for {user['user_id']}: {e}")
            user_list += f"- User ID: {user['user_id']} (Deleted Account or Blocked)\n"

    sent_list_message = await client.send_message(chat_id, user_list)
    await message.delete()

    await asyncio.sleep(15)
    await sent_list_message.delete()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@bot.on_message(filters.command("graph"))
async def graph_command(client, message: Message):
    args = message.text.split()
    timeframe = args[1] if len(args) > 1 else "24h"
    try:
        path = await generate_and_plot_graph(timeframe)
        sent = await message.reply_photo(photo=path, caption=f"📊 Bio Link Checks Over Last `{timeframe}`", quote=True)
        
        # Optionally wait before deleting (like 10 seconds)
        await asyncio.sleep(10)
        
        os.remove(path)  # Optional: clean up the local image file

    except Exception as e:
        await message.reply_text(f"❌ Error generating graph:\n{e}")


async def generate_and_plot_graph(timeframe: str = "24h"):
    log_file = "bio_hits_log.txt"
    if not os.path.exists(log_file):
        raise FileNotFoundError("bio_hits_log.txt not found.")

    # Load and prepare data
    df = pd.read_csv(log_file, names=["timestamp", "user_id"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    now = datetime.utcnow()
    if timeframe.endswith("h"):
        delta = timedelta(hours=int(timeframe[:-1]))
    elif timeframe.endswith("d"):
        delta = timedelta(days=int(timeframe[:-1]))
    else:
        raise ValueError("Use format like `6h`, `3d`, or `30d`.")

    df = df[df.index >= now - delta]
    resampled = df["user_id"].resample("1Min").count()

    # Construct OHLC
    ohlc = pd.DataFrame({
        "Open": resampled.shift(1).fillna(0),
        "High": resampled.rolling(2).max().fillna(0),
        "Low": resampled.rolling(2).min().fillna(0),
        "Close": resampled.fillna(0)
    }).dropna()

    if ohlc.shape[0] > 1:
        ohlc = ohlc.iloc[:-1]

    # Reset index for plotting
    ohlc.reset_index(inplace=True)
    ohlc["timestamp_num"] = mdates.date2num(ohlc["timestamp"])

    # Color logic based on Close value trend
    close_values = ohlc["Close"].values
    colors = []
    for i in range(len(close_values)):
        if i == 0:
            colors.append("gray")
        elif close_values[i] > close_values[i - 1]:
            colors.append("green")
        elif close_values[i] < close_values[i - 1]:
            colors.append("red")
        else:
            colors.append("gray")  # no change

    # Plot using matplotlib
    fig, ax = plt.subplots(figsize=(10, 4))
    width = 0.0008  # Candle width in matplotlib date units

    if ohlc.empty:
        # If no data, show red line at y=0
        ax.axhline(0, color="red", linestyle="--", linewidth=2)
    else:
        for i, row in ohlc.iterrows():
            low = row["Low"]
            high = row["High"]
            open_ = row["Open"]
            close = row["Close"]
            color = colors[i]

            if open_ == close and high == low:
                continue  # skip flat candles

            # Wick
            ax.plot([row["timestamp_num"], row["timestamp_num"]], [low, high], color=color, linewidth=1)

            # Body
            ax.add_patch(plt.Rectangle(
                (row["timestamp_num"] - width / 2, min(open_, close)),
                width,
                max(0.5, abs(open_ - close)),  # minimum height for visibility
                color=color
            ))

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.title(f"Bio Link Checks - Last {timeframe}")
    plt.ylabel("Checks / Min")
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    path = f"bio_hits_candle_{timeframe}.png"
    plt.savefig(path)
    plt.close()

    return path




async def has_link_in_bio(user_id: int):
    """Check if user's bio has a link with MongoDB-based cooldown and logs each hit."""

    now = time.time()
    user_data = bio_cooldown_collection.find_one({"user_id": user_id})
    last_checked = user_data.get("last_checked", 0) if user_data else 0

    # Log every time this function is called (optional: only if it's a new check)
    if now - last_checked >= 15:
        with open("bio_hits_log.txt", "a") as log_file:
            timestamp = datetime.utcnow().isoformat()
            log_file.write(f"{timestamp},{user_id}\n")

    if now - last_checked < 15:
        cached_result = user_data.get("has_link") if user_data else None
        return cached_result if cached_result is not None else False

    try:
        user = await bot.get_chat(user_id)
        bio = user.bio or ""
        has_link = bool(re.search(r"(https?://\S+|t\.me/\S+|@\S+|\b\w+\.\w{2,}\b)", bio))

        bio_cooldown_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_checked": now, "has_link": has_link}},
            upsert=True
        )

        return has_link

    except FloodWait as e:
        logging.info(f"[FloodWait] Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        return await has_link_in_bio(user_id)

    except Exception as e:
        logging.error(f"Error fetching bio for {user_id}: {e}")
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# async def has_link_in_bio(user_id: int):
#     """Check if user's bio has a link with MongoDB-based 4-second cooldown."""

#     now = time.time()

#     # Find the user's last check time
#     user_data = bio_cooldown_collection.find_one({"user_id": user_id})
#     last_checked = user_data.get("last_checked", 0) if user_data else 0

#     # If it's been less than 4 seconds, return cached result if we have it
#     if now - last_checked < 15:
#         cached_result = user_data.get("has_link") if user_data else None
#         return cached_result if cached_result is not None else False

#     try:
#         user = await bot.get_chat(user_id)
#         bio = user.bio or ""
#         has_link = bool(re.search(r"(https?://\S+|t\.me/\S+|@\S+|\b\w+\.\w{2,}\b)", bio))

#         # Update Mongo with result and timestamp
#         bio_cooldown_collection.update_one(
#             {"user_id": user_id},
#             {"$set": {"last_checked": now, "has_link": has_link}},
#             upsert=True
#         )

#         return has_link

#     except FloodWait as e:
#         logging.info(f"[FloodWait] Sleeping for {e.value} seconds")
#         await asyncio.sleep(e.value)
#         return await has_link_in_bio(user_id)  # Retry

#     except Exception as e:
#         logging.error(f"Error fetching bio for {user_id}: {e}")
#         return False



@bot.on_message(filters.group & ~filters.bot, group=1)
async def check_bio_links(client: Client, message: Message):
    if not message.from_user:  # Ensure from_user exists
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        # Fetch and cache admin list
        admins = await is_admins(chat_id)
        if user_id in admins:  # Skip if user is admin
            return

        # Check if user is BonusUsers and allow up to 2 messages
        user_data = bonus_collection.find_one({"user_id": user_id})
        if user_data and user_data["message_count"] < 2:
            bonus_collection.update_one(
                {"user_id": user_id}, {"$inc": {"message_count": 1}}
            )
            return

        # Check if group has the no-bio-link restriction and if user is whitelisted
        if not nobiolink_collection.find_one({"chat_id": chat_id}) or whitelisted_users_collection.find_one({"chat_id": chat_id, "user_id": user_id}):
            return

        if await has_link_in_bio(user_id):
            await message.delete()

            # If user is NOT in bonus_collection, show the button
            reply_markup = None
            if not user_data:
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("See Magic✨", url=f"https://t.me/{bot.me.username}?start=true")]
                ])

            reply_message = await message.reply_text(
                f"> Hey [{message.from_user.first_name}](tg://user?id={message.from_user.id}), your message was deleted because your bio contains a link.",
                reply_markup=reply_markup
            )

            await asyncio.sleep(15)
            await reply_message.delete()

    except Exception as e:
        logging.error(f"Error in check_bio_links: {e}")


















# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.on_message(filters.command("logs") & filters.private)
async def toggle_logs(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if user is a bot admin
    if user_id not in config.BOT_ADMINS:
        return await message.reply_text("❌ You are not authorized to use this command.")

    # Toggle the logs setting
    current_setting = logs_control_collection.find_one({"_id": "logs"})
    if current_setting and current_setting.get("enabled"):
        logs_control_collection.update_one({"_id": "logs"}, {"$set": {"enabled": False}})
        await message.reply_text("📴 Logging has been **disabled**.")
    else:
        logs_control_collection.update_one(
            {"_id": "logs"}, {"$set": {"enabled": True}}, upsert=True
        )
        await message.reply_text("📢 Logging has been **enabled**.")

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.on_message(filters.command("stats") & filters.group)
async def stats(client, message):
    bot_info = await client.get_me()
    bot_name = bot_info.first_name  # Fetch bot's name

    await message.delete()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Show Stats", callback_data="show_stats")]
    ])

    # Image URL or local path
    image_url = "https://biolinksdetector.github.io/Bot/src/stats.png"  # Replace with your image link or local path

    # Send an image with the bot stats message
    stats_message = await client.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption=f"{bot_name} Stats",
        reply_markup=keyboard
    )

    # Wait for 20 seconds, then delete the message
    await asyncio.sleep(20)
    await stats_message.delete()


@bot.on_message(filters.command("stats") & filters.private)
async def stats(client, message):
    if message.from_user.id not in config.BOT_ADMINS:  # Use config.BOT_ADMINS
        return  # Do nothing if not an admin

    bot_info = await client.get_me()
    bot_name = bot_info.first_name  # Fetch bot's name

    await message.delete()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Show Stats", callback_data="show_stats")]
    ])

    # Image URL or local path
    image_url = "https://biolinksdetector.github.io/Bot/src/stats.png"

    # Send an image with the bot stats message
    await client.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption=f"{bot_name} Stats",
        reply_markup=keyboard
    )

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.on_callback_query(filters.regex("show_stats"))
async def show_stats(client, callback_query: CallbackQuery):
    uptime = time.time() - start_time
    days = int(uptime // 86400)
    hours = int((uptime % 86400) // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    uptime_parts = []
    if days > 0:
        uptime_parts.append(f"{days}d")
    if hours > 0:
        uptime_parts.append(f"{hours}h")
    if minutes > 0:
        uptime_parts.append(f"{minutes}m")
    if seconds > 0 or not uptime_parts:
        uptime_parts.append(f"{seconds}s")
    
    uptime_str = " ".join(uptime_parts)
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent

    # Fetch total counts from the database
    total_users = users_collection.count_documents({})
    total_chats = chats_collection.count_documents({})

    stats_text = f"""
 ⏳ Uptime: {uptime_str}
 💾 Memory Usage: {memory_usage}%
 🔥 CPU Usage: {cpu_usage}%
 💬 Total Chats: {total_chats}
 👥 Total Users: {total_users}
"""
    await callback_query.answer(stats_text, show_alert=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

broadcasting = False  # Global flag to track broadcast status

async def is_bot_admin(user_id: int):
    return user_id in config.BOT_ADMINS

@bot.on_message(filters.command("broadcast"))
async def broadcast_message(client, message):
    global broadcasting
    if not await is_bot_admin(message.from_user.id):
        return  # Ignore if user is not an admin

    if message.reply_to_message:
        broadcast_message = message.reply_to_message  # Forward the entire message
    elif len(message.command) > 1:
        broadcast_text = message.text.split(None, 1)[1]
    else:
        broadcast_text = None

    if not message.reply_to_message and not broadcast_text:
        usage_instructions = (
            "Usage: /broadcast {message} or reply to a message with /broadcast\n\n"
            "Example: `/broadcast Hello Guys`"
        )
        await message.reply_text(usage_instructions)
        return  # Exit if no message is provided

    users_list = [chat for chat in users_collection.find() if chat.get("user_id") not in config.BOT_ADMINS]
    total_users = len(users_list)
    total_seconds = total_users * 2
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    estimated_time = (f"{hours}h {minutes}m {seconds}s" if hours else
                      f"{minutes}m {seconds}s" if minutes else
                      f"{seconds}s")

    # Inform admin about the estimated time
    await message.reply_text(f"> 📢 **Broadcast in Progress**\n\n"
                             f"> ⏳ Estimated Time: **{estimated_time}**\n"
                             f"> 👥 Total Recipients: **{total_users} users**\n\n"
                             f"Please wait while messages are being delivered...")

    sent_users, failed_users = 0, 0
    broadcasting = True

    for chat in users_list:
        if not broadcasting:
            break  # Stop broadcasting if the flag is set to False

        chat_id = chat.get("user_id")
        chat_id = int(chat_id) if chat_id else None

        if chat_id is None:
            logging.error(f"Error in check_bio_links: {e}")  # Debugging log
            continue

        try:
            logging.info(f"🔍 Sending message to: {chat_id}")
            if message.reply_to_message:
                await message.reply_to_message.forward(chat_id)  # Forward the original message
            else:
                await client.send_message(chat_id, broadcast_text)
            sent_users += 1
            await asyncio.sleep(2)  # Small delay to prevent spam blocking
        except Exception as e:
            logging.error(f"⚠️ Failed to send message to {chat_id}: {e}")
            failed_users += 1

    summary_message = (f"> ✅ **Broadcast Summary**\n\n"
                       f"📩 Successfully Sent: **{sent_users}**\n"
                       f"⚠️ Failed Deliveries: **{failed_users}**")
    
    await message.reply_text(summary_message)


@bot.on_message(filters.command("stop"))
async def stop_broadcast(client, message):
    global broadcasting
    if not await is_bot_admin(message.from_user.id):
        return  # Ignore if user is not an admin

    if not broadcasting:
        await message.reply_text("ℹ️ **Nothing is Broadcasting.**")
        return

    broadcasting = False
    await message.reply_text("⛔ **Broadcasting has been stopped.**")

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Function to run the speed test
def testspeed(m: Message):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit_text("⚙️ Testing download speed...")
        test.download()
        m = m.edit_text("⚙️ Testing upload speed...")
        test.upload()
        test.results.share()
        result = test.results.dict()
        m = m.edit_text("📤 Sharing results...")
    except speedtest.ConfigRetrievalError:
        return m.edit_text("❌ Could not retrieve server configuration. Try again later.")
    except speedtest.SpeedtestHTTPError as e:
        return m.edit_text(f"❌ Speedtest blocked the request (403 Forbidden).")
    except Exception as e:
        return m.edit_text(f"❌ Unexpected error:\n<code>{e}</code>")
    return result

# Pyrogram command handler
@bot.on_message(filters.command(["speedtest", "spt"]) & filters.user(config.BOT_ADMINS))
async def speedtest_function(client: Client, message: Message):
    await message.delete()
    m = await message.reply_text("📡 Running speedtest, please wait...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)

    if not isinstance(result, dict):
        return  # Error already handled

    output = (
        "🏁 <b>Speedtest Results</b>\n\n"
        f"🌐 <b>ISP:</b> {result['client']['isp']}\n"
        f"🌍 <b>Country:</b> {result['client']['country']}\n\n"
        f"📡 <b>Server:</b> {result['server']['name']} "
        f"({result['server']['country']}, {result['server']['cc']})\n"
        f"🏢 <b>Sponsor:</b> {result['server']['sponsor']}\n"
        f"⚡️ <b>Latency:</b> {result['server']['latency']} ms\n"
        f"📶 <b>Ping:</b> {result['ping']} ms"
    )

    await message.reply_photo(photo=result["share"], caption=output)
    await m.delete()

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

logging.info("✅ The bot is running successfully.")
bot.run()

