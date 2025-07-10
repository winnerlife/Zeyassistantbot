# In modules/help.py

import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# Get the bot's username from the environment variables
BOT_USERNAME = os.environ.get("TG_BOT_USERNAME")

@Client.on_message(filters.command(["hhelp", "hh"], prefix) & filters.me)
async def trigger_inline_help(client: Client, message: Message):
    """Triggers the inline help menu from the companion bot."""
    if not BOT_USERNAME:
        return await message.edit("<b>Help Bot not configured (TG_BOT_USERNAME missing).</b>")
    
    try:
        # Ask the bot for its inline results
        results = await client.get_inline_bot_results(BOT_USERNAME, "help")
        if not results:
             return await message.edit("<b>Could not fetch inline help menu. Is the assistant bot running?</b>")

        # Send the first result (our main menu)
        await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"<b>Error triggering help:</b> <code>{e}</code>")

# You can add the other simple help commands (.hcmds, .hdc, etc.) here if you wish.
# For simplicity, we'll just add the main one for now.

modules_help["help"] = {
    "hhelp": "Shows the interactive help menu via the helper bot.",
}