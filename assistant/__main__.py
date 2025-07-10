# In assistant/__main__.py

import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    InlineQueryResultArticle, InputTextMessageContent
)

# We need to access the main userbot's config for API credentials.
# The '..' tells Python to look one directory up.
from ..utils import config
from ..utils.misc import modules_help, prefix
from ..utils.scripts import format_module_help

# --- BOT CONFIGURATION ---
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
BOT_USERNAME = os.environ.get("TG_BOT_USERNAME")

if not BOT_TOKEN or not BOT_USERNAME:
    print("[ASSISTANT ERROR] TG_BOT_TOKEN or TG_BOT_USERNAME not set. The assistant bot cannot start.")
    exit()

# Initialize the assistant bot client
bot = Client(
    name="my_assistant_bot_session",
    api_id=config.api_id,
    api_hash=config.api_hash,
    bot_token=BOT_TOKEN
)

# --- BOT HANDLERS (The bot's brain) ---

@bot.on_inline_query()
async def inline_help_handler(client: Client, query: CallbackQuery):
    """Responds to the userbot's inline query with the main help menu."""
    text = "<b>Userbot Help Menu</b>\n\nSelect a module below to get a list of its commands."
    await query.answer(
        results=[
            InlineQueryResultArticle(
                title="Open Help Menu",
                description="Displays the main help interface.",
                input_message_content=InputTextMessageContent(text),
                reply_markup=get_main_help_keyboard()
            )
        ],
        cache_time=1
    )

@bot.on_callback_query(filters.regex("^bothelp_"))
async def bot_callback_handler(client: Client, query: CallbackQuery):
    """Handles all button clicks for the help menu."""
    data = query.data.split(":")[1]

    if data == "main":
        text = "<b>Userbot Help Menu</b>\n\nSelect a module below to get a list of its commands."
        await query.edit_message_text(text, reply_markup=get_main_help_keyboard())
    elif data == "close":
        await query.message.delete()
    else: # It's a module name
        text = format_module_help(data, prefix)
        await query.edit_message_text(text, reply_markup=get_back_button("main"))

# --- KEYBOARD HELPERS ---

def get_main_help_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        InlineKeyboardButton(
            module_name.capitalize(),
            callback_data=f"bothelp:{module_name}"
        ) for module_name in sorted(modules_help.keys())
    ]
    rows = [keyboard[i:i + 3] for i in range(0, len(keyboard), 3)]
    rows.append([InlineKeyboardButton("❌ Close", callback_data="bothelp:close")])
    return InlineKeyboardMarkup(rows)

def get_back_button(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data=f"bothelp:{callback}")]]
    )

# --- Main startup function for the bot ---
async def start_assistant():
    print("Starting Assistant Bot...")
    await bot.start()
    print("Assistant Bot is now online.")
    await idle()
    await bot.stop()
    print("Assistant Bot stopped.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_assistant())
