import asyncio
import re
import os

# You must install this library: pip install lyricsgenius
import lyricsgenius

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified

from utils.misc import modules_help, prefix

# --- Configuration ---
# IMPORTANT: Place your Genius API Token here.
# It's recommended to use an environment variable for security.
# Example: GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN")
GENIUS_API_TOKEN = "YOUR_GENIUS_API_TOKEN_HERE" 

# Initialize the Genius API client
# The 'verbose=False' and 'remove_section_headers=True' options clean up the output.
try:
    genius = lyricsgenius.Genius(GENIUS_API_TOKEN, verbose=False, remove_section_headers=True)
except Exception as e:
    genius = None
    print(f"Could not initialize Genius API. Is the token valid? Error: {e}")

# --- Helper for animated text ---
async def edit_with_animation(message: Message, text: str, delay: float = 0.1):
    """Simple animation for 'Searching...'"""
    for i in range(4):
        await message.edit(text + "." * i)
        await asyncio.sleep(delay)

# --- Lyrics Command Handler ---
@Client.on_message(filters.command("lyrics", prefix) & filters.me)
async def sing_lyrics(client: Client, message: Message):
    if not genius:
        await message.edit("`Genius API is not configured. Please add a valid token.`")
        await asyncio.sleep(3)
        await message.delete()
        return

    # --- 1. Parse Input ---
    if len(message.command) < 2:
        await message.edit("`Please provide a song title. Usage: .lyrics [song] by [artist]`")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    # Rejoin the command parts and split by "by" to separate song and artist
    query = " ".join(message.command[1:])
    try:
        # We assume the format is "song title by artist"
        song_title, artist = query.rsplit(" by ", 1)
        song_title = song_title.strip()
        artist = artist.strip()
    except ValueError:
        # If "by" is not found, we use the whole query as the song title
        # and let Genius try to figure it out.
        song_title = query
        artist = ""

    # --- 2. Searching Animation ---
    try:
        await message.edit("🔎 `Searching...`")
    except MessageNotModified:
        pass # Ignore if the message is already the same

    # --- 3. Fetch Lyrics ---
    try:
        song = genius.search_song(song_title, artist)
        if song is None:
            await message.edit(f"❌ **Song not found for:** `{query}`")
            await asyncio.sleep(4)
            await message.delete()
            return
    except Exception as e:
        await message.edit(f"An error occurred while searching: `{e}`")
        await asyncio.sleep(4)
        await message.delete()
        return

    # --- 4. Prepare and "Sing" Lyrics ---
    lyrics_text = song.lyrics
    # Clean up the first line which is often just "[Song Title] Lyrics"
    lyrics_text = re.sub(r'.*?Lyrics\n', '', lyrics_text, 1)
    # Also clean potential "Embed" lines at the end
    lyrics_text = re.sub(r'\d*Embed$', '', lyrics_text).strip()

    lines = [line for line in lyrics_text.split('\n') if line.strip() != '']

    await message.edit(f'▶️ **NOW PLAYING:** "{song.title}" by **{song.artist}**')
    await asyncio.sleep(2)

    try:
        for line in lines:
            words = line.split()
            current_line_text = ""
            
            # Don't sing lines that are too long to avoid hitting Telegram limits
            if len(line) > 4000:  # Telegram message character limit is 4096
                continue

            # Animate word by word
            for word in words:
                current_line_text += f" {word}"
                # Use a very short delay for a fast "typing" effect
                animation_speed = 0.25 # seconds per word
                
                try:
                    # The microphone emoji adds a nice touch
                    await message.edit(f"🎤 `{current_line_text.strip()}`")
                    await asyncio.sleep(animation_speed)
                except FloodWait as e:
                    # If we get floodwaited, wait the specified time
                    await asyncio.sleep(e.value)
                except MessageNotModified:
                    # If the word is the same as the last one, just continue
                    continue
            
            # Pause slightly longer at the end of a line
            await asyncio.sleep(1.5)

    except Exception:
        # If anything goes wrong during the animation (e.g., message deleted)
        # we just stop silently.
        return
    
    # --- 5. Finalization ---
    await asyncio.sleep(5)
    await message.delete()


# --- Add to Help Dictionary ---
modules_help["lyrics"] = {
    "lyrics [song title] by [artist]": "Finds and 'sings' the lyrics of a song word-by-word.",
}
