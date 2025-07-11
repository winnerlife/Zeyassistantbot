import os
import asyncio
import aiohttp
import tempfile
import shutil
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
import instaloader

# Your Instagram cookies (same as before)
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

# Rate limiting storage
last_request_time = {}

async def rate_limit_check(user_id):
    """Check and enforce rate limiting (30 seconds between requests)"""
    current_time = asyncio.get_event_loop().time()
    
    if user_id in last_request_time:
        time_diff = current_time - last_request_time[user_id]
        if time_diff < 30:  # 30 seconds cooldown
            return False, 30 - time_diff
    
    last_request_time[user_id] = current_time
    return True, 0

async def get_specific_post(username, post_index, client, chat_id, message):
    """Get specific post (Xth latest) from Instagram profile."""
    
    # Add human-like delay at start
    await asyncio.sleep(random.uniform(2, 5))
    
    await message.edit(f"📱 Fetching post #{post_index} from @{username}...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize instaloader with more human-like settings
        L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_comments=False,
            download_geotags=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=temp_dir,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        
        # Load session with cookies
        L.context._session.cookies.update(COOKIES)
        
        # Add random delay before profile fetch
        await asyncio.sleep(random.uniform(1, 3))
        
        # Get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        if profile.is_private:
            await message.edit(f"❌ @{username} is a private account")
            return False
            
        await message.edit(f"📥 Found @{username}\nSearching for post #{post_index}...")
        
        # Add delay before fetching posts
        await asyncio.sleep(random.uniform(2, 4))
        
        # Get the specific post (Xth latest)
        target_post = None
        for idx, post in enumerate(profile.get_posts(), 1):
            if idx == post_index:
                target_post = post
                break
            # Add small delay between post checks to seem more human
            if idx % 5 == 0:  # Every 5 posts
                await asyncio.sleep(random.uniform(0.5, 1.5))
        
        if not target_post:
            await message.edit(f"❌ Post #{post_index} not found for @{username}")
            return False
            
        await message.edit(f"📤 Downloading post #{post_index} from @{username}...")
        
        # Add delay before download
        await asyncio.sleep(random.uniform(1, 3))
        
        # Download post media
        L.download_post(target_post, target='')
        
        # Find downloaded files for this post
        downloaded_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.startswith(f"{target_post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC"):
                    if file.endswith(('.jpg', '.jpeg', '.png', '.mp4', '.webm')):
                        downloaded_files.append(os.path.join(root, file))
        
        # Sort files to maintain order
        downloaded_files.sort()
        
        # Prepare simplified caption
        caption = f"📸 Post #{post_index} by @{username}\n\n"
        
        if target_post.caption:
            # Limit caption length
            caption_text = target_post.caption[:400] + "..." if len(target_post.caption) > 400 else target_post.caption
            caption += f"💬 {caption_text}\n\n"
        
        caption += f"📅 {target_post.date_utc.strftime('%Y-%m-%d %H:%M UTC')}\n"
        caption += f"🔗 https://instagram.com/p/{target_post.shortcode}"
        
        # Send media files with human-like delays
        if downloaded_files:
            # Separate photos and videos
            photos = [f for f in downloaded_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            videos = [f for f in downloaded_files if f.lower().endswith(('.mp4', '.webm', '.mov'))]
            
            # Add delay before sending
            await asyncio.sleep(random.uniform(1, 2))
            
            # Send photos as media group if multiple
            if photos:
                if len(photos) == 1:
                    await client.send_photo(chat_id, photos[0], caption=caption)
                else:
                    # Send as media group
                    from pyrogram.types import InputMediaPhoto
                    media_group = []
                    for i, photo in enumerate(photos):
                        if i == 0:
                            media_group.append(InputMediaPhoto(photo, caption=caption))
                        else:
                            media_group.append(InputMediaPhoto(photo))
                    await client.send_media_group(chat_id, media_group)
            
            # Send videos separately with delay
            for video in videos:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                video_caption = caption if not photos else None
                await client.send_video(chat_id, video, caption=video_caption)
                        
        else:
            # If no files downloaded, send text message
            await client.send_message(chat_id, caption)
        
        return True
        
    except instaloader.exceptions.ProfileNotExistsException:
        await message.edit(f"❌ Profile @{username} does not exist")
        return False
    except instaloader.exceptions.LoginRequiredException:
        await message.edit("❌ Login required - cookies may be expired")
        return False
    except Exception as e:
        await message.edit(f"❌ Error fetching post:\n<code>{str(e)}</code>")
        return False
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@Client.on_message(filters.command("insta", prefix) & filters.me)
async def instagram_specific_post(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Usage: <code>.insta [username] [post_number]</code>\nExample: <code>.insta username 5</code> (gets 5th latest post)")
        return

    username = message.command[1].replace("@", "")  # Remove @ if present
    
    # Parse post index (default to 1st latest)
    post_index = 1
    if len(message.command) >= 3:
        try:
            post_index = int(message.command[2])
            if post_index < 1:
                await message.edit("❌ Post number must be at least 1")
                return
            if post_index > 100:
                await message.edit("❌ Post number cannot exceed 100")
                return
        except ValueError:
            await message.edit("❌ Invalid post number. Please enter a valid number.")
            return
    
    # Rate limiting check
    user_id = message.from_user.id
    can_proceed, wait_time = await rate_limit_check(user_id)
    
    if not can_proceed:
        await message.edit(f"⏱️ Rate limit: Please wait {wait_time:.0f} seconds before next request")
        return
    
    success = await get_specific_post(username, post_index, client, message.chat.id, message)
    
    if success:
        await message.delete()
    # Error messages are already sent in the function

modules_help["insta"] = {
    "insta [username] [post_number]": "Get specific post (Xth latest) from Instagram profile. Default: 1st latest post."
}