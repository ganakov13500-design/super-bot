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

# Настройки источника и интервала
SOURCE_GROUP_ID = -204081884  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id.txt'

# 1. ТОКЕН ДЛЯ ЧТЕНИЯ 
READ_TOKEN = 'vk1.a.ezI_5MZF-3M53uwZ5z1uPr6Ge6xdFOgxVQ3ki0hfXO-NlpPkjPTR6Q_nNS_4uGHZtcAiKIxix_XC1hFqLjcQKcGH004RY86ZtJypWl872BK4cbF-BoLca2xU0RaeQkt82TJxAto9bJeWwwSp2Zl82ttitq9I1SeyRERKWfCCVCQdCQv_L-mYHrMG8Z9-d9F8IJEHWWWchiZ48XNMnIBsPw'

# 2. ТОКЕН ДЛЯ ПУБЛИКАЦИИ (Админский токен профиля)
WRITE_TOKEN = 'vk1.a.DfdvCntvdJ-m4AzB23YnnoX-bcL96v1Uo1UN_h4_xgw0MQcMfYVdmdtlw4V2Vg_2cl-xsGtOX-Cj7g5Rp5nWBLsgSXCe2vubynyXfDpaPXjfxuXckj3lyu0lOEaAENKvhNx8fWnu4s-3NQfqyH-0mR4hm9uW56yDDsi0qQpnW-ecsmyIn6sFcAPyeSci0VA9aDNzcS5lUsJKs25MJWTJXQ'

# 3. СПИСОК ЦЕЛЕВЫХ ГРУПП
TARGET_GROUP_IDS = [
    -215578086, 
    -221202163, 
    -219647526, 
    -219649455, 
    -215622579
]

# 🔥 ФИКСАЦИЯ СЧЕТЧИКА НА 15107 🔥
def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            try: 
                val = int(file.read().strip())
                if val < 15107:
                    print(f"[Бот 2] Текущий кэш ({val}) меньше целевого. Принудительно устанавливаем на 15107!")
                    return 15107
                return val
            except ValueError: 
                return 15107
    return 15107

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w') as file:
        file.write(str(post_id))

def run_bot_vk_2():
    print("Авторизация ВКонтакте (Бот 2)...")
    
    try:
        vk_read_session = vk_api.VkApi(token=READ_TOKEN)
        vk_reader = vk_read_session.get_api()
        print("[Успех] Сессия для чтения исходной группы создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Не удалось создать сессию чтения. Детали: {e}")
        return

    try:
        vk_write_session = vk_api.VkApi(token=WRITE_TOKEN)
        vk_writer = vk_write_session.get_api()
        print("[Успех] Сессия пользователя-администратора создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Не удалось создать сессию публикации. Детали: {e}")
        return

    last_post_id = get_saved_last_post_id()
    print(f"Бот ВК 2 запущен. В памяти ID прошлого поста: {last_post_id}")
    print(f"Готов к публикации в {len(TARGET_GROUP_IDS)} групп(ы).")

    while True:
        try:
            response = vk_reader.wall.get(owner_id=SOURCE_GROUP_ID, count=2)
            posts = response['items']
            if not posts:
                print(f"[Бот 2] Стена донора пуста. Ждем {CHECK_INTERVAL} сек.")
                time.sleep(CHECK_INTERVAL)
                continue

            current_post = next((p for p in posts if not p.get('is_pinned')), posts[0])
            current_post_id = current_post['id']

            print(f"[Бот 2 ПРОВЕРКА] ID на стене: {current_post_id} | ID в памяти: {last_post_id}")

            if last_post_id == 0:
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print(f"[Бот 2] Это ПЕРВЫЙ запуск. Запомнили пост {last_post_id}. Публиковать НЕ БУДЕМ. Ждем новый пост.")
            
            elif current_post_id <= last_post_id:
                print(f"[Бот 2] Новых постов нет (на стене {current_post_id} <= {last_post_id}). Ухожу в сон.")
                
            elif current_post_id > last_post_id:
                print(f"\n[Бот 2] НАЙДЕН НОВЫЙ ПОСТ: {current_post_id}! Начинаю обработку медиа...")
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
                            
                            # Если есть и ID владельца, и ID файла — собираем строку для ВК
                            if owner_id and media_id:
                                att_str = f"{att_type}{owner_id}_{media_id}"
                                if item.get('access_key'): 
                                    att_str += f"_{item.get('access_key')}"
                                extracted.append(att_str)
                    return extracted

                # 1. Извлекаем медиа из обычного поста
                if 'attachments' in current_post:
                    attachments_list.extend(extract_attachments(current_post['attachments']))
                
                # 2. Если это РЕПОСТ, извлекаем текст и медиа из оригинального поста
                if 'copy_history' in current_post and len(current_post['copy_history']) > 0:
                    repost = current_post['copy_history'][0]
                    
                    # Добавляем текст репоста, если он есть
                    if not post_text and repost.get('text'):
                        post_text = repost['text']
                        
                    # Добавляем картинки/видео из репоста
                    if 'attachments' in repost:
                        attachments_list.extend(extract_attachments(repost['attachments']))

                attachments_str = ','.join(attachments_list)
                print(f"[Бот 2] Собрано вложений: {len(attachments_list)}")
                # ---------------------------------------------
                
                for target_id in TARGET_GROUP_IDS:
                    try:
                        vk_writer.wall.post(
                            owner_id=target_id, 
                            from_group=1, 
                            message=post_text, 
                            attachments=attachments_str
                        )
                        print(f"  -> Успешно отправлено в {target_id}")
                        
                        sleep_time = random.randint(15, 40)
                        print(f"  -> Антиспам: ждем {sleep_time} сек...")
                        time.sleep(sleep_time)
                        
                    except Exception as e:
                        print(f"  -> Ошибка отправки в {target_id}: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print("[Бот 2] Рассылка завершена. Возвращаюсь в режим ожидания.")

        except Exception as e:
            print(f"[Бот 2] Общая ошибка проверки постов: {e}")
        
        final_wait = CHECK_INTERVAL + random.randint(10, 90)
        time.sleep(final_wait)

if __name__ == '__main__':
    run_bot_vk_2()
    
