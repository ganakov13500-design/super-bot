import vk_api
import time
import os
import asyncio
import aiohttp
import io  # Добавлена библиотека для работы с байтами
from maxapi import Bot

VK_TOKEN = 'vk1.a.7bP--MARwJ67rtpJY2TF1s4I8r5MvGlWyNZf0faRGyS5lvXB900G7NnEgkcqtXc8X1bMThqo0pJ-zEou77gCgC47BdbfWMSkfC0bmvnzVPSdDmnv5nOC56ABHH-qmj4E-OmFlNI1kmY54i1MXeaTEYJEICZuxm7tBf2OuqvPHIRJztrNaAzEeKJapW_ILRWD2kaas9Cn1qCHEjVXm8ZO9Q'
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
                    
                    # Упаковываем байты в виртуальный файл
                    photo_file = io.BytesIO(media_data)
                    photo_file.name = 'photo.jpg'
                    
                    # Теперь maxapi должна корректно принять фото
                    await bot.send_photo(chat_id=channel_id, photo=photo_file, caption=text if text else None)
                    return True
    except Exception as e: 
        # Теперь ошибка не будет тихой, вы увидите ее в консоли
        print(f"[Ошибка отправки фото МАКС]: {e}")
        return False

async def process_new_post(post):
    post_text = post.get('text', '')
    photos = []
    videos = []

    # Собираем все фото и формируем ссылки на видео
    if 'attachments' in post:
        for att in post['attachments']:
            if att['type'] == 'photo':
                photos.append(get_max_photo_url(att['photo']['sizes']))
            elif att['type'] == 'video':
                video_owner = att['video']['owner_id']
                video_id = att['video']['id']
                videos.append(f"https://vk.com/video{video_owner}_{video_id}")

    # Если в посте есть видео, аккуратно добавляем ссылки на них вниз текста
    if videos:
        post_text += "\n\n🎥 Видео в посте:\n" + "\n".join(videos)

    for channel_id in TARGET_MAX_CHANNELS:
        try:
            if photos:
                # Отправляем первое фото вместе с общим текстом
                success = await download_and_send_media(photos[0], post_text, channel_id)
                if not success: 
                    await bot.send_message(chat_id=channel_id, text=post_text)
                
                # Если фотографий в посте несколько, отправляем остальные следом
                for extra_photo in photos[1:]:
                    await asyncio.sleep(1)
                    await download_and_send_media(extra_photo, "", channel_id)
                    
            elif post_text:
                await bot.send_message(chat_id=channel_id, text=post_text)
            
            await asyncio.sleep(2) 
        except Exception as e: 
            print(f"[Ошибка МАКС канал {channel_id}]: {e}")

def run_bot_max():
    print("Авторизация (Бот МАКС)...")
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        vk.groups.getById() 
        print("[Успех] Бот МАКС авторизован ВКонтакте.")
    except Exception as e: 
        print(f"[Ошибка] Авторизация ВК (Бот МАКС) не удалась: {e}")
        return

    last_post_id = get_saved_last_post_id()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print(f"Бот МАКС запущен. Последний пост: {last_post_id}")

    while True:
        try:
            response = vk.wall.get(owner_id=SOURCE_VK_GROUP_ID, count=2)
            posts = response['items']
            if not posts: 
                time.sleep(CHECK_INTERVAL)
                continue

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
        except Exception as e: 
            print(f"[Бот МАКС] Ошибка получения постов: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    run_bot_max()
