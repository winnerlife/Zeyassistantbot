from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# --- Global variable to store the bot's start time ---
START_TIME = datetime.now()


async def get_bot_version(client: Client) -> str:
    """Fetches the bot version from a specific message in the MY_PLAYLIST group."""
    try:
        target_chat_id = None
        async for dialog in client.get_dialogs():
            if dialog.chat and dialog.chat.title == "MY_PLAYLIST":
                target_chat_id = dialog.chat.id
                break

        if not target_chat_id:
            return "Chat 'MY_PLAYLIST' not found"

        async for message in client.get_chat_history(target_chat_id, limit=200):
            if message.text and message.text.upper().startswith("BOT_VERSION:"):
                return message.text.split(":", 1)[1].strip()

        return "Version message not found"

    except ChatAdminRequired:
        return "Not an admin in chat"
    except Exception as e:
        return f"Error: {e.__class__.__name__}"


async def get_alive_media(client: Client) -> tuple[str, str] | None:
    """
    Fetches the media for the alive command from the MY_PLAYLIST group.
    Looks for a photo or animation with the caption "ALIVE_IMAGE".
    Returns a tuple of (media_type, file_id) if found, otherwise None.
    """
    try:
        target_chat_id = None
        async for dialog in client.get_dialogs():
            if dialog.chat and dialog.chat.title == "MY_PLAYLIST":
                target_chat_id = dialog.chat.id
                break

        if not target_chat_id:
            return None

        async for message in client.get_chat_history(target_chat_id, limit=200):
            # Check for caption first
            if message.caption and message.caption.upper() == "ALIVE_IMAGE":
                # Then check if it's a photo or an animation (GIF)
                if message.photo:
                    return "photo", message.photo.file_id
                elif message.animation:
                    return "animation", message.animation.file_id

        return None
    except Exception:
        return None


def get_readable_time(seconds: int) -> str:
    """Converts a duration in seconds to a human-readable string."""
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    (hours, remainder) = divmod(remainder, 3600)
    (minutes, seconds) = divmod(remainder, 60)

    if days > 0: result += f"{days}d "
    if hours > 0: result += f"{hours}h "
    if minutes > 0: result += f"{minutes}m "
    if result == "" or seconds > 0: result += f"{seconds}s"
    return result.strip()


@Client.on_message(filters.command("alive", prefix) & filters.me)
async def alive_command(client: Client, message: Message):
    """Check if the userbot is running and show system status, with media."""
    try:
        await message.edit("✨ Checking pulse...")

        start_time = datetime.now()
        await client.get_me()
        end_time = datetime.now()
        latency = (end_time - start_time).microseconds / 1000

        me = await client.get_me()
        owner_name = f"{me.first_name} {me.last_name or ''}".strip()
        bot_version = await get_bot_version(client)
        uptime_str = get_readable_time(int((datetime.now() - START_TIME).total_seconds()))
        current_date = datetime.now().strftime("%Y-%m-%d")

        alive_text = (
            "𝕀'𝕞 𝕒𝕝𝕚𝕧𝕖 𝕒𝕟𝕕 𝕗𝕦𝕟𝕔𝕥𝕚𝕠𝕟𝕚𝕟𝕘!\n\n\n"
            f"|—————ｷﾘﾄﾘｾﾝ—————\n☆\n"
                  f"☆——»» вoт verѕιoɴ: {bot_version}\n"
            f"☆——»» dαтe: {current_date}\n"
            f"☆——»» υp ѕιɴce: {uptime_str}\n"
            f"☆——»» owɴer: {owner_name}\n☆\n"
            f"|—————ｷﾘﾄﾘｾﾝ—————\n\n\n\n"

            f"» ριηg: {latency:.2f}ms"
)

        media_info = await get_alive_media(client)

        if media_info:
            media_type, file_id = media_info
            
            # Use the correct send method based on the media type
            if media_type == "photo":
                await client.send_photo(message.chat.id, file_id, caption=alive_text)
            elif media_type == "animation":
                await client.send_animation(message.chat.id, file_id, caption=alive_text)
            
            await message.delete()
        else:
            fallback_text = alive_text + "\n\n*(Note: No alive media found)*"
            await message.edit(fallback_text)

    except Exception as e:
        await message.edit(format_exc(e))


modules_help["alive"] = {
    "alive": "Check if the bot is running and show system status."
}