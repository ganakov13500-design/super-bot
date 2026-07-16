import vk_api
import time
import os

TOKEN = 'vk1.a.7xkUXPha1U9ea2vVvl4_4LWsyIYf8sJca1Jrh45wQCNtvFMLgA_70bJYCbncS9txJXqv3bwFj_rMz9UXG3I8jG5_8XfYMQKhgAc8wGJ7Q1ShPOqyx3jiivdoL-DQaFf12Sm_2HFqRkphKRO_54Lhs3x_OvqJZkpQuHXXPl7SrLQ4mDF8GlU50iFT86tujuuXYjEUZULIGagEl6vZqWTIbA'
SOURCE_GROUP_ID = -218341918  
TARGET_GROUP_IDS = [-225274463]  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id_2.txt'

def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            try: return int(file.read().strip())
            except ValueError: return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w') as file:
        file.write(str(post_id))

def run_bot_vk_1():
    print("Авторизация ВКонтакте (Бот 1)...")
    try:
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        # Проверка авторизации через метод для сообществ
        vk.groups.getById() 
    except Exception as e:
        print(f"Ошибка авторизации (Бот 1). Убедитесь, что используете токен группы. Детали: {e}")
        return

    last_post_id = get_saved_last_post_id()
    print(f"Бот ВК 1 запущен. Последний пост: {last_post_id}")

    while True:
        try:
            response = vk.wall.get(owner_id=SOURCE_GROUP_ID, count=2)
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
                print(f"[Бот 1] Найден новый пост: {current_post_id}.")
                post_text = current_post.get('text', '')
                attachments_list = []
                if 'attachments' in current_post:
                    for att in current_post['attachments']:
                        att_type = att['type']
                        if att_type in ['photo', 'video', 'doc', 'audio']:
                            item = att[att_type]
                            att_str = f"{att_type}{item.get('owner_id')}_{item.get('id')}"
                            if item.get('access_key'): att_str += f"_{item.get('access_key')}"
                            attachments_list.append(att_str)
                
                attachments_str = ','.join(attachments_list)
                
                for target_id in TARGET_GROUP_IDS:
                    try:
                        # from_group=1 означает публикацию от имени самой группы
                        vk.wall.post(owner_id=target_id, from_group=1, message=post_text, attachments=attachments_str)
                        print(f"[Бот 1] Пост успешно опубликован в {target_id}.")
                        time.sleep(3) 
                    except Exception as e:
                        print(f"[Бот 1] Ошибка публикации: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)

        except Exception as e:
            print(f"[Бот 1] Ошибка получения постов: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    run_bot_vk_1()
