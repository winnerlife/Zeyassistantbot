import os
import asyncio
import aiohttp
import json
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from utils.misc import modules_help, prefix
import instaloader

# Your Instagram cookies (we'll convert these to instaloader format)
COOKIES = {
    'ig_did': 'CAF03226-256D-4D21-916B-9B35C487E8D3',
    'datr': 'ywbYZjsmGvYYp8wm6ksn6Q5u',
    'ig_nrcb': '1',
    'mid': 'Z-jEGgALAAG5GNvJTGGO4Ayo_D8S',
    'dpr': '1.25',
    'csrftoken': '71uQcCJqVOkI5KuVbMFUmGIZ2hvvaiRA',
    'ds_user_id': '75868557198',
    'wd': '1536x776',
    'sessionid': '75868557198%3AUi50jgLfCVQUE7%3A23%3AAYeZ8P_CUcMrYUdJPfXh45YkNNig5V5X2BtnkM4pAg',
    'rur': '"CLN\05475868557198\0541783451685:01fe2ebcabce4c7673db7b24e28b730c53d7375d2a04781d6c6a37696c23dcf127a02d29"'
}

async def download_with_instaloader(url, client, chat_id, message):
    """Download Instagram post using instaloader with cookies."""
    await message.edit("📥 Downloading with instaloader...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize instaloader
        L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_comments=False,
            download_geotags=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=temp_dir
        )
        
        # Load session with cookies
        L.context._session.cookies.update(COOKIES)
        
        # Extract shortcode from URL
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            await message.edit("❌ Invalid Instagram URL format")
            return False
            
        # Get post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Download post
        await message.edit(f"📥 Downloading post by @{post.owner_username}...")
        L.download_post(post, target='')
        
        # Find downloaded files
        downloaded_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.jpg', '.jpeg', '.png', '.mp4', '.webm')):
                    downloaded_files.append(os.path.join(root, file))
        
        if not downloaded_files:
            await message.edit("❌ No media files found after download")
            return False
            
        await message.edit(f"📤 Sending {len(downloaded_files)} file(s)...")
        
        # Send files
        for file_path in downloaded_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.mp4', '.webm', '.mov']:
                await client.send_video(chat_id, file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                await client.send_photo(chat_id, file_path)
            else:
                await client.send_document(chat_id, file_path)
        
        return True
        
    except Exception as e:
        await message.edit(f"❌ Instaloader error:\n<code>{str(e)}</code>")
        return False
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

async def scrape_photos_fallback(url, client, chat_id, message):
    """Fallback scraper to get photos from a public Instagram post."""
    await message.edit("🔍 Trying fallback scraper...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Cookie": "; ".join([f"{k}={v}" for k, v in COOKIES.items()])
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await message.edit(f"❌ Failed to fetch page (status {resp.status})")
                    return False
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag:
            await message.edit("❌ Could not find JSON data on page.")
            return False

        data = json.loads(script_tag.string)

        try:
            media = data["props"]["pageProps"]["graphql"]["shortcode_media"]
        except Exception:
            await message.edit("❌ Unexpected page structure, cannot find media info.")
            return False

        photos = []

        # Carousel posts
        if media.get("edge_sidecar_to_children"):
            edges = media["edge_sidecar_to_children"]["edges"]
            for edge in edges:
                node = edge["node"]
                if not node.get("is_video"):
                    photos.append(node.get("display_url"))
        else:
            # Single media post
            if not media.get("is_video", False):
                photos.append(media.get("display_url"))

        if not photos:
            await message.edit("❌ No photos found.")
            return False

        await message.edit(f"📥 Downloading {len(photos)} photo(s)...")

        for idx, photo_url in enumerate(photos, 1):
            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url, headers=headers) as resp:
                    if resp.status != 200:
                        continue
                    photo_bytes = await resp.read()

            await client.send_photo(chat_id, photo_bytes, caption=f"Photo {idx}")

        return True

    except Exception as e:
        await message.edit(f"❌ Fallback scraper error:\n<code>{e}</code>")
        return False


@Client.on_message(filters.command("igdl", prefix) & filters.me)
async def instagram_downloader(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Usage: <code>.igdl [Instagram URL]</code>")
        return

    url = message.command[1]
    
    # Try instaloader first
    success = await download_with_instaloader(url, client, message.chat.id, message)
    
    if not success:
        # Try fallback scraper
        await message.edit("🔄 Trying fallback method...")
        success = await scrape_photos_fallback(url, client, message.chat.id, message)
    
    if success:
        await message.delete()
    else:
        await message.edit("❌ All download methods failed.")


modules_help["igdl"] = {
    "igdl [instagram_url]": "Download Instagram posts and reels using instaloader + fallback scraper."
}