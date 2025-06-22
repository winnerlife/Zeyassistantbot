#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

from utils.misc import modules_help, prefix

# --- State variable for the dontsleep command ---
dontsleep_status = {
    "is_running": False,
    "chat_id": None,
    "message_id": None,
}

# --- Existing Spam Commands ---
spam_commands = ["spam", "statspam", "slowspam", "fastspam"]

@Client.on_message(filters.command(spam_commands, prefix) & filters.me)
async def spam(client: Client, message: Message):
    # (Your existing spam code remains unchanged)
    amount = int(message.command[1])
    text = " ".join(message.command[2:])
    cooldown = {"spam": 0.15, "statspam": 0.1, "slowspam": 0.9, "fastspam": 0}
    await message.delete()
    for _msg in range(amount):
        if message.reply_to_message:
            sent = await message.reply_to_message.reply(text)
        else:
            sent = await client.send_message(message.chat.id, text)
        if message.command[0] == "statspam":
            await asyncio.sleep(0.1)
            await sent.delete()
        await asyncio.sleep(cooldown[message.command[0]])

# --- Existing Check Command ---
@Client.on_message(filters.command("check", prefix) & filters.me)
async def countdown(client: Client, message: Message):
    # (Your existing countdown code remains unchanged)
    await message.edit("🔟")
    await asyncio.sleep(1)
    for i in range(10, -1, -1):
        await message.edit(f"**{i}**")
        await asyncio.sleep(1)
    await message.edit("🚀 **Blast off!**")
    await asyncio.sleep(3)
    await message.delete()


# --- NEW: Background task to update the time ---
async def time_updater(client: Client):
    while dontsleep_status.get("is_running"):
        try:
            # Format the current time as HH:MM:SS
            current_time = datetime.now().strftime("%H:%M:%S")
            text = f"🕰️ **Time:** `{current_time}`\n\n*This message will self-destruct when stopped.*"

            # Edit the message
            await client.edit_message_text(
                chat_id=dontsleep_status["chat_id"],
                message_id=dontsleep_status["message_id"],
                text=text,
            )
        except MessageNotModified:
            # This error happens if the text is the same (unlikely here), we can ignore it
            pass
        except Exception:
            # If any other error occurs (e.g., message deleted), stop the loop
            dontsleep_status["is_running"] = False
            return
        
        # Wait for 1 second before the next update
        await asyncio.sleep(1)

# --- NEW: dontsleep command handler ---
@Client.on_message(filters.command("dontsleep", prefix) & filters.me)
async def start_dontsleep(client: Client, message: Message):
    if dontsleep_status["is_running"]:
        await message.edit("`dontsleep` is already running!")
        await asyncio.sleep(2)
        await message.delete()
        return

    # Set the status and store the message details
    dontsleep_status["is_running"] = True
    dontsleep_status["chat_id"] = message.chat.id
    dontsleep_status["message_id"] = message.id
    
    # Start the background task
    asyncio.create_task(time_updater(client))
    
    await message.edit("`dontsleep` mode activated. Use `.ddontsleep` to stop.")

# --- NEW: ddontsleep command handler ---
@Client.on_message(filters.command("ddontsleep", prefix) & filters.me)
async def stop_dontsleep(client: Client, message: Message):
    if not dontsleep_status["is_running"]:
        await message.edit("`dontsleep` is not running.")
        await asyncio.sleep(2)
        await message.delete()
        return

    # Signal the background task to stop
    dontsleep_status["is_running"] = False
    
    # Edit the original message to a final "stopped" state
    try:
        await client.edit_message_text(
            chat_id=dontsleep_status["chat_id"],
            message_id=dontsleep_status["message_id"],
            text="✅ **Stopped.**",
        )
        # Optional: Delete the "stopped" message after a delay
        await asyncio.sleep(3)
        await client.delete_messages(
            chat_id=dontsleep_status["chat_id"],
            message_ids=dontsleep_status["message_id"],
        )
    except Exception:
        # Fails silently if the original message was already deleted
        pass
    
    # Delete the .ddontsleep command itself
    await message.delete()


# --- Updated Help Dictionary ---
modules_help["spam"] = {
    "spam [amount] [text]": "Start spam",
    "statspam [amount] [text]": "Send and delete",
    "fastspam [amount] [text]": "Start fast spam",
    "slowspam [amount] [text]": "Start slow spam",
    "check": "Starts a 10 second countdown.",
    "dontsleep": "Shows a real-time clock that updates every second.",
    "ddontsleep": "Stops the `dontsleep` clock.",
}
