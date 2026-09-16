import vk_api
import time
import os
import builtins
import random

# --- ХАК ДЛЯ ПРИНУДИТЕЛЬНОГО ВЫВОДА ЛОГОВ В RENDER ---
def print(*args, **kwargs):
    kwargs['flush'] = True
    builtins.print(*args, **kwargs)
# -----------------------------------------------------

# 1. ТОКЕН ДЛЯ ЧТЕНИЯ (фейковый/дополнительный аккаунт)
READ_TOKEN = 'vk1.a.ezI_5MZF-3M53uwZ5z1uPr6Ge6xdFOgxVQ3ki0hfXO-NlpPkjPTR6Q_nNS_4uGHZtcAiKIxix_XC1hFqLjcQKcGH004RY86ZtJypWl872BK4cbF-BoLca2xU0RaeQkt82TJxAto9bJeWwwSp2Zl82ttitq9I1SeyRERKWfCCVCQdCQv_L-mYHrMG8Z9-d9F8IJEHWWWchiZ48XNMnIBsPw'

# 2. ТОКЕН ДЛЯ ПУБЛИКАЦИИ 
WRITE_TOKEN = 'vk1.a.ev-6nDQqkhKAByZBoyIdTCrgqIB_btajDrjCRfMQGoDJh79nCN8oFtsIMnt9QU1wN8UJNhVsJQduZEpQ7OCXT4Y2GRoCcYUkYLXTUD4fcl05-gdrs8fZGNHNCYdCLcM3kCH3lastGbYNTeBMctmM1YES4B5vZ53hORiDyKjn9HwWwPVO-8ce5Q6hZ8IbAgY3Jxp2lGvqQJeiQfXkN-3k1g'

SOURCE_GROUP_ID = -218341918  
TARGET_GROUP_IDS = [-225274463]  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id_2.txt'

def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r', encoding='utf-8') as file:
            try: 
                return int(file.read().strip())
            except ValueError: 
                return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w', encoding='utf-8') as file:
        file.write(str(post_id))

def run_bot_vk_1():
    print("Авторизация ВКонтакте (Бот 1)...")
    
    # Инициализация сессии для ЧТЕНИЯ (донора)
    try:
        vk_read_session = vk_api.VkApi(token=READ_TOKEN)
        vk_reader = vk_read_session.get_api()
        print("[Успех] Бот 1: Сессия для чтения создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Бот 1: Ошибка читающего аккаунта. Детали: {e}")
        return

    # Инициализация сессии для ПУБЛИКАЦИИ (группа/админ)
    try:
        vk_write_session = vk_api.VkApi(token=WRITE_TOKEN)
        vk_writer = vk_write_session.get_api()
        # Проверка прав доступа к целевой группе
        vk_writer.groups.getById(group_id=abs(TARGET_GROUP_IDS[0])) 
        print(f"[Успех] Бот 1: Целевая группа {TARGET_GROUP_IDS[0]} доступна для публикации.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Бот 1: Ошибка сессии публикации. Детали: {e}")
        return

    last_post_id = get_saved_last_post_id()
    print(f"Бот ВК 1 запущен. Последний сохраненный пост: {last_post_id}")

    while True:
        try:
            # Читаем через vk_reader (токен чтения)
            response = vk_reader.wall.get(owner_id=SOURCE_GROUP_ID, count=2)
            posts = response['items']
            if not posts:
                print(f"[Бот 1] Стена пуста. Ожидание...")
                time.sleep(CHECK_INTERVAL)
                continue

            current_post = next((p for p in posts if not p.get('is_pinned')), posts[0])
            current_post_id = current_post['id']

            if last_post_id == 0:
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print(f"[Бот 1] Первый запуск. Запомнили пост: {last_post_id}. Ждем новые.")
            
            elif current_post_id <= last_post_id:
                # Тихо ждем, если новых постов нет (без лишнего спама в консоль)
                pass
                
            elif current_post_id > last_post_id:
                print(f"\n[Бот 1] НАЙДЕН НОВЫЙ ПОСТ: {current_post_id}! Подготовка к копированию...")
                post_text = current_post.get('text', '')
                attachments_list = []
                
                # --- УЛУЧШЕННАЯ ФУНКЦИЯ ИЗВЛЕЧЕНИЯ МЕДИА ---
                def extract_attachments(attachments_data):
                    extracted = []
                    for att in attachments_data:
                        att_type = att.get('type')
                        if att_type in ['photo', 'video', 'doc', 'audio']:
                            item = att.get(att_type, {})
                            owner_id = item.get('owner_id')
                            media_id = item.get('id')
                            
                            # Безопасная проверка на None
                            if owner_id is not None and media_id is not None:
                                att_str = f"{att_type}{owner_id}_{media_id}"
                                if item.get('access_key'): 
                                    att_str += f"_{item.get('access_key')}"
                                extracted.append(att_str)
                    return extracted

                # 1. Извлекаем медиа из обычного поста
                if 'attachments' in current_post:
                    attachments_list.extend(extract_attachments(current_post['attachments']))
                
                # 2. Обработка репоста (copy_history)
                if 'copy_history' in current_post and len(current_post['copy_history']) > 0:
                    repost = current_post['copy_history'][0]
                    # Добавляем текст репоста, если основного текста нет
                    if not post_text and repost.get('text'):
                        post_text = repost['text']
                    # Добавляем вложения из репоста
                    if 'attachments' in repost:
                        attachments_list.extend(extract_attachments(repost['attachments']))

                attachments_str = ','.join(attachments_list)
                
                # Публикация по целевым группам
                for target_id in TARGET_GROUP_IDS:
                    try:
                        # Пишем через vk_writer (токен с правами публикации)
                        vk_writer.wall.post(
                            owner_id=target_id, 
                            from_group=1, 
                            message=post_text, 
                            attachments=attachments_str
                        )
                        print(f"  -> [Бот 1] Пост успешно опубликован в {target_id}.")
                        
                        # Антиспам пауза
                        sleep_time = random.randint(30, 60)
                        print(f"  -> [Бот 1] Антиспам: пауза {sleep_time} сек...")
                        time.sleep(sleep_time)
                        
                    except Exception as e:
                        print(f"  -> [Бот 1] Ошибка публикации в {target_id}: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print("[Бот 1] Обработка поста завершена.")

        except Exception as e:
            print(f"[Бот 1] Ошибка получения постов: {e}")
        
        # Динамическая задержка проверки для имитации человека
        final_wait = CHECK_INTERVAL + random.randint(10, 60)
        time.sleep(final_wait)

if __name__ == '__main__':
    run_bot_vk_1()
