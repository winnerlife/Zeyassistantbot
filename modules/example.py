#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import re

# httpx is a dependency of Pyrogram, so no new installation is needed.
import httpx 

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified

from utils.misc import modules_help, prefix


# --- Helper Function to Scrape Lyrics from AZLyrics ---
async def fetch_lyrics_from_az(artist: str, title: str) -> str | None:
    """
    Scrapes lyrics from AZLyrics.com using httpx.
    Returns the lyrics as a string, or None if not found.
    """
    # Sanitize inputs for the URL format of AZLyrics
    # e.g., "Guns N' Roses" -> "gunsnroses"
    artist_f = re.sub(r'[^a-z0-9]', '', artist.lower())
    title_f = re.sub(r'[^a-z0-9]', '', title.lower())
    
    url = f"https://www.azlyrics.com/lyrics/{artist_f}/{title_f}.html"
    
    # AZLyrics blocks requests without a valid User-Agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    try:
        # Use an async context manager for the client
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None # Song not found (404) or other error
            
            html_content = response.text

        # The lyrics are between a specific comment and a </div> tag.
        # This is brittle and will break if AZLyrics changes their website layout.
        start_marker = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
        end_marker = "</div>"
        
        lyrics_block = html_content.split(start_marker)[1]
        lyrics_raw = lyrics_block.split(end_marker)[0]
        
        # Clean up the HTML tags from the raw lyrics
        lyrics_cleaned = re.sub(r'<br> ?', '\n', lyrics_raw) # Replace <br> with newlines
        lyrics_cleaned = re.sub(r'</?i>', '', lyrics_cleaned)  # Remove <i> and </i> tags
        lyrics_cleaned = lyrics_cleaned.strip()

        return lyrics_cleaned

    except (httpx.RequestError, IndexError):
        # IndexError will happen if the split markers are not found (song not on site)
        return None


# --- Main Command Handler for Lyrics ---
@Client.on_message(filters.command("lyrics", prefix) & filters.me)
async def sing_lyrics_scraper(client: Client, message: Message):
    # --- 1. Parse Input ---
    if len(message.command) < 2:
        await message.edit("`Please provide a song title. Usage: .lyrics [song] by [artist]`")
        await asyncio.sleep(3)
        await message.delete()
        return

    query = " ".join(message.command[1:])
    try:
        song_title, artist = query.rsplit(" by ", 1)
        song_title = song_title.strip()
        artist = artist.strip()
    except ValueError:
        await message.edit("`Invalid format. Please use: .lyrics [song] by [artist]`")
        await asyncio.sleep(3)
        await message.delete()
        return

    # --- 2. Searching Animation ---
    search_msg = "🔎 `Searching...`"
    await message.edit(search_msg)
    for i in range(1, 4):
        await asyncio.sleep(0.3)
        try:
            await message.edit(search_msg + "." * i)
        except MessageNotModified:
            pass

    # --- 3. Fetch Lyrics using our scraper ---
    lyrics_text = await fetch_lyrics_from_az(artist, song_title)
    
    if lyrics_text is None:
        await message.edit(f"❌ **Song not found for:** `{song_title} by {artist}`")
        await asyncio.sleep(4)
        await message.delete()
        return

    # --- 4. Prepare and "Sing" Lyrics ---
    lines = [line for line in lyrics_text.split('\n') if line.strip() != '']

    await message.edit(f'▶️ **NOW PLAYING:** "{song_title.title()}" by **{artist.title()}**')
    await asyncio.sleep(2)

    try:
        for line in lines:
            words = line.split()
            current_line_text = ""
            
            if len(line) > 4000: continue # Skip very long lines to avoid Telegram errors

            # Animate word by word
            for word in words:
                current_line_text += f" {word}"
                animation_speed = 0.25
                
                try:
                    await message.edit(f"🎤 `{current_line_text.strip()}`")
                    await asyncio.sleep(animation_speed)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except MessageNotModified:
                    continue
            
            await asyncio.sleep(1.5) # Pause at the end of a line

    except Exception:
        return # Stop silently if an error occurs (e.g., message deleted)
    
    # --- 5. Finalization ---
    await asyncio.sleep(5)
    await message.delete()


# This adds instructions for your module to the global .help command
modules_help["lyrics"] = {
    "lyrics [song title] by [artist]": "Finds lyrics from AZLyrics and 'sings' them word-by-word.",
}
