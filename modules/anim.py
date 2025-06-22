from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["ping", "p"], prefix) & filters.me)
async def ping(client: Client, message: Message):
    latency = await client.ping()
    await message.edit(f"<b>Pong! {latency}ms</b>")


modules_help["ping"] = {
    "ping": "Check ping to Telegram servers",
}
