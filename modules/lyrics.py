import asyncio
import re

# httpx is a dependency of Pyrogram, so no new installation is needed.
import httpx 

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified

from utils.misc import modules_help, prefix

# --- Helper Function to Scrape Lyrics ---
async def fetch_lyrics_from_az(artist: str, title: str) -> str | None:
    """
    Scrapes lyrics from AZLyrics.com.
    Returns the lyrics as a string, or None if not found.
    """
    # Sanitize inputs for the URL format of AZLyrics
    # e.g., "Guns N' Roses" -> "gunsnroses"
    artist_f = re.sub(r'[^a-z0-9]', '', artist.lower())
    title_f = re.sub(r'[^a-z0-9]', '', title.lower())
    
    url = f"https://www.azlyrics.com/lyrics/{artist_f}/{title_f}.html"
    
    # AZLyrics blocks requests without a valid User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            # If the song is not found, AZLyrics returns a 404
            if response.status_code != 200:
                return None
            
            html_content = response.text

        # --- This is the core scraping logic ---
        # The lyrics are between a specific comment and a </div> tag.
        # This is brittle and will break if AZLyrics changes their layout.
        start_marker = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
        end_marker = "</div>"
        
        # Split the HTML to isolate the lyrics block
        lyrics_block = html_content.split(start_marker)[1]
        lyrics_raw = lyrics_block.split(end_marker)[0]
        
        # Clean up the HTML tags from the raw lyrics
        lyrics_cleaned = re.sub(r'<br> ?', '\n', lyrics_raw) # Replace <br> with newlines
        lyrics_cleaned = re.sub(r'</?i>', '', lyrics_cleaned)  # Remove <i> and </i> tags
        lyrics_cleaned = lyrics_cleaned.strip()
        
        # It's better to also decode HTML entities, but this requires the 'html' library.
        # For simplicity and to meet the "no new imports" rule, we'll skip it.
        # lyrics_cleaned = html.unescape(lyrics_cleaned)

        return lyrics_cleaned

    except (httpx.RequestError, IndexError):
        # IndexError will happen if the split markers are not found
        return None


# --- Lyrics Command Handler ---
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
        # This will fail if " by " isn't in the query, which is a good hint
        await message.edit("`Invalid format. Please use: .lyrics [song] by [artist]`")
        await asyncio.sleep(3)
        await message.delete()
        return

    # --- 2. Searching Animation ---
    search_msg = "🔎 `Searching...`"
    await message.edit(search_msg)
    # Simple dot animation
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
            
            if len(line) > 4000: continue # Skip very long lines

            # Animate word by word
            for word in words:
                current_line_text += f" {word}"
                animation_speed = 0.25 # seconds per word
                
                try:
                    await message.edit(f"🎤 `{current_line_text.strip()}`")
                    await asyncio.sleep(animation_speed)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except MessageNotModified:
                    continue
            
            await asyncio.sleep(1.5) # Pause at the end of a line

    except Exception:
        return # Stop silently if an error occurs
    
    # --- 5. Finalization ---
    await asyncio.sleep(5)
    await message.delete()


# --- Add to Help Dictionary ---
modules_help["lyrics"] = {
    "lyrics [song title] by [artist]": "Finds lyrics from AZLyrics and 'sings' them word-by-word.",
}
