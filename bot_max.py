import vk_api
import time
import os
import asyncio
import aiohttp
from maxapi import Bot

VK_TOKEN = 'vk1.a.psMq_CslP7UkHUuCDtpCjMpqxaVREyN2i8VRTTC9IbKS0USTRQSzhknMXftF56g5Asm_D67j7tEY__IKlq6ZPsW6NzaqXJol_HPZ9lVkHIkv2VrJEvcTxbp6bZIHW8-emz0l8jjWoXBiR6vJbeeNnCUzu7DWsPYJgl2JCik-7GIw8za7xqjZVjGkfXfMtami3Bq6R2krJz8LcvJZSFaa8g'
SOURCE_VK_GROUP_ID = -204081884  
MAX_BOT_TOKEN = 'f9LHodD0cOL81vMNbHAKhY6E8unklP9ERiZH1WN4qu0gTsUj1Dl6p6FUEd9OiiPXcvebPXREXcVP684jEawY'
TARGET_MAX_CHANNELS = ['-69296966003283', '-69205136755442', '-69209774882901', '-69207050491139', '-69224752493851']
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_vk_post_for_max.txt'

bot = Bot(token=MAX_BOT_TOKEN)

def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            try: return int(file.read().strip())
            except ValueError: return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w') as file:
        file.write(str(post_id))

def get_max_photo_url(sizes):
    max_size, max_url = 0, ""
    for size in sizes:
        if size['height'] * size['width'] > max_size:
            max_size = size['height'] * size['width']
            max_url = size['url']
    return max_url

async def download_and_send_media(media_url, text, channel_id):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(media_url) as response:
                if response.status == 200:
                    media_data = await response.read()
                    await bot.send_photo(chat_id=channel_id, photo=media_data, caption=text if text else None)
                    return True
    except Exception: return False

async def process_new_post(post):
    post_text = post.get('text', '')
    media_url = None
    if 'attachments' in post:
        for att in post['attachments']:
            if att['type'] == 'photo':
                media_url = get_max_photo_url(att['photo']['sizes'])
                break

    for channel_id in TARGET_MAX_CHANNELS:
        try:
            if media_url:
                success = await download_and_send_media(media_url, post_text, channel_id)
                if not success: await bot.send_message(chat_id=channel_id, text=post_text)
            elif post_text:
                await bot.send_message(chat_id=channel_id, text=post_text)
            await asyncio.sleep(2) 
        except Exception: pass

def run_bot_max():
    print("Авторизация (Бот МАКС)...")
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        vk.users.get() 
    except Exception as e: return

    last_post_id = get_saved_last_post_id()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            response = vk.wall.get(owner_id=SOURCE_VK_GROUP_ID, count=2)
            posts = response['items']
            if not posts: continue

            current_post = next((p for p in posts if not p.get('is_pinned')), posts[0])
            current_post_id = current_post['id']

            if last_post_id == 0:
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
            elif current_post_id > last_post_id:
                print(f"[Бот МАКС] Найден новый пост: {current_post_id}!")
                loop.run_until_complete(process_new_post(current_post))
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
        except Exception as e: print(f"[Бот МАКС] Ошибка: {e}")
        time.sleep(CHECK_INTERVAL)
