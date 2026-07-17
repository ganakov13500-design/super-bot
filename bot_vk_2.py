import vk_api
import time
import os

# Настройки источника и интервала
SOURCE_GROUP_ID = -204081884  
CHECK_INTERVAL = 300  # 5 минут
LAST_POST_FILE = 'last_post_id.txt'
API_VERSION = '5.131' # Обязательно указываем свежую версию API

# ВСТАВЬ СЮДА НОВЫЕ СГЕНЕРИРОВАННЫЕ ТОКЕНЫ!
READ_TOKEN = 'ТВОЙ_НОВЫЙ_ТОКЕН_ПОЛЬЗОВАТЕЛЯ'

TARGET_GROUPS = {
    -215578086: 'НОВЫЙ_ТОКЕН_ГРУППЫ_1',
    -221202163: 'НОВЫЙ_ТОКЕН_ГРУППЫ_2',
    -219647526: 'НОВЫЙ_ТОКЕН_ГРУППЫ_3',
    -219649455: 'НОВЫЙ_ТОКЕН_ГРУППЫ_4',
    -215622579: 'НОВЫЙ_ТОКЕН_ГРУППЫ_5'
}

def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            try: 
                return int(file.read().strip())
            except ValueError: 
                return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w') as file:
        file.write(str(post_id))

def run_bot_vk_2():
    print("Инициализация сессий ВКонтакте (Бот 2)...")
    
    # 1. Создаем сессию для ЧТЕНИЯ донора
    try:
        vk_read_session = vk_api.VkApi(token=READ_TOKEN, api_version=API_VERSION)
        vk_reader = vk_read_session.get_api()
        print("[Успех] Сессия для чтения исходной группы создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Не удалось создать сессию для чтения: {e}")
        return

    vk_sessions = {}
    
    # 2. Авторизуем каждую группу по её токену для ПУБЛИКАЦИИ
    for group_id, token in TARGET_GROUPS.items():
        try:
            vk_session = vk_api.VkApi(token=token, api_version=API_VERSION)
            api = vk_session.get_api()
            
            # Проверяем токен: если токен не от той группы, он выдаст ошибку
            api.groups.getById(group_id=abs(group_id))
            vk_sessions[group_id] = api
            print(f"[Успех] Группа {group_id} авторизована.")
        except Exception as e:
            print(f"[Ошибка] Не удалось авторизовать группу {group_id}. Детали: {e}")

    if not vk_sessions:
        print("Ни одна целевая группа не авторизована. Скрипт остановлен.")
        return

    last_post_id = get_saved_last_post_id()
    
    # Кастомный сброс ID (оставил твою логику)
    if last_post_id == 481928: 
        last_post_id = 14991

    print(f"Бот 2 запущен. Готов к публикации в {len(vk_sessions)} групп(ы).")
    print(f"Последний известный ID поста: {last_post_id if last_post_id > 0 else 'Нет (первый запуск)'}")

    while True:
        try:
            # Читаем стену донора
            response = vk_reader.wall.get(owner_id=SOURCE_GROUP_ID, count=2)
            posts = response['items']
            
            if not posts:
                time.sleep(CHECK_INTERVAL)
                continue

            # Ищем первый незакрепленный пост
            current_post = next((p for p in posts if not p.get('is_pinned')), posts[0])
            current_post_id = current_post['id']

            # ЛОГИКА ПЕРВОГО ЗАПУСКА
            if last_post_id == 0:
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print(f"[Бот 2] Первый запуск. Запомнили текущий пост (ID: {last_post_id}). Ожидаем новые посты...")
            
            # ЕСЛИ ПОСТ НОВЫЙ
            elif current_post_id > last_post_id:
                print(f"\n[Бот 2] Найден новый пост: {current_post_id}. Начинаю рассылку...")
                post_text = current_post.get('text', '')
                attachments_list = []
                
                # Парсим вложения
                if 'attachments' in current_post:
                    for att in current_post['attachments']:
                        att_type = att['type']
                        if att_type in ['photo', 'video', 'doc', 'audio']:
                            item = att[att_type]
                            att_str = f"{att_type}{item.get('owner_id')}_{item.get('id')}"
                            if item.get('access_key'): 
                                att_str += f"_{item.get('access_key')}"
                            attachments_list.append(att_str)
                
                attachments_str = ','.join(attachments_list)
                
                # Публикуем во все группы
                for target_id, vk_writer in vk_sessions.items():
                    try:
                        vk_writer.wall.post(
                            owner_id=target_id, 
                            from_group=1, 
                            message=post_text, 
                            attachments=attachments_str
                        )
                        print(f"  -> Пост успешно опубликован в {target_id}")
                        time.sleep(3)  # Антиспам пауза
                    except Exception as e:
                        print(f"  -> [Ошибка] Не удалось опубликовать в {target_id}: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print("[Бот 2] Рассылка завершена. Возвращаюсь в режим ожидания.")

        except Exception as e:
            print(f"[Бот 2] Ошибка при проверке стены: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    run_bot_vk_2()
    
