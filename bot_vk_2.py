import vk_api
import time
import os

# Настройки источника и интервала
SOURCE_GROUP_ID = -204081884  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id.txt'

# ТОКЕН ДЛЯ ЧТЕНИЯ (Сервисный ключ доступа приложения или токен пользователя)
# Обязателен, так как токены групп не могут читать чужие стены!
READ_TOKEN = 'vk1.a.epwD7Tqgk2kINMbv14Txirhpeyhtdk-vRy4aaq-cSPAInHyQJDBe-g1ldP9zLUWKHPNLV8Yv1DURke8iRSvO0sGoaLpCIH6OI9ffpLSNtxBPpkjtjT4sZHHTnsdQB31syV0hJA6tv0wyhvNoy5XHVKH0ZdZTLSSVOUm4E3FWebRXWXO0vU5ymaI1rCwoMuH3zh2lR2t-uI8a-vKM0nRw5w'

# Словарь: {ID_ЦЕЛЕВОЙ_ГРУППЫ: 'ЕЁ_УНИКАЛЬНЫЙ_ТОКЕН'}
TARGET_GROUPS = {
    -215578086: 'vk1.a.7bP--MARwJ67rtpJY2TF1s4I8r5MvGlWyNZf0faRGyS5lvXB900G7NnEgkcqtXc8X1bMThqo0pJ-zEou77gCgC47BdbfWMSkfC0bmvnzVPSdDmnv5nOC56ABHH-qmj4E-OmFlNI1kmY54i1MXeaTEYJEICZuxm7tBf2OuqvPHIRJztrNaAzEeKJapW_ILRWD2kaas9Cn1qCHEjVXm8ZO9Q',
    -221202163: 'vk1.a.ppOEGD2uuS9imHz627zgVwkrlBvnBwAjYgYwu4ZKVSEm3D5R_fuwqNB09WJujE9XGIxS-BM8h1hTxurv4BfjQ49QPKXnmVxeVZrKwOZFTVAYtubopEVfON038WqNXLHGTvpXRB9Bh7N0PaBeDgFd3-vXe2EWffS6sQC8_MaSFfcmWjKqZIOduVomcuZdm7s7WwS2EbDr_A6O4l7LQ3Mqnw',
    -219647526: 'vk1.a.LUbRHqYwwF0NudOwykToMCLp64DxJEbfYdB-vhWKQpaqLPMijnoL1IBT9Z2khOqO59o7b7TtnWE6--j8g22l-_84H8hBdTEbgd7X8pig6orDW0CMGmT94AkRwvahuSVlPzvoSmX0tgfjK8jfexNNmS-ZgFc2Z_QbFpJu-nMK7FpNZHcDqc-t0snoKyZF6MonUVdp_jveG_5peif7Zm3i8w',
    -219649455: 'vk1.a.UbTW2Br60aeXRWawLvQu6kNcsb1Khls0lLjMrfOT99XAsHbNVcrXg8ZdlUN-vdcmdloiSgAKWGJph24OkOUekDitA7NnyCSJPmmbatVSlrpjH80FfoUzO-sQVi2pOdpJcU7uw_7yYn7j7367ZmvO1CYDkqo-tqabTr-v0yTp9nS0ZluFqYjtEcsbJWAoSkkPjaI7HTlNeu9xf74WP6SFVw',
    -215622579: 'vk1.a.uPE6HPrHtsm3UQIcAjL67s75hoLxyvWX8p4ta1HOyleZcR7cdhtVG11BPr505k1pn2pElTSf3JMF4VBfYdMKYM9z1FcXcnZ_TQrpuR_EaQlydqcnlotqR-yr-8u9mza--uEr6Sjo9it9PzRYECROV75G_8A3TYW1AJ_TJ4mM0DQeetOBOefDzL_tgd3OwJ5P2sMFesxOZESN7ciRUVjq-Q'
}

def get_saved_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            try: return int(file.read().strip())
            except ValueError: return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, 'w') as file:
        file.write(str(post_id))

def run_bot_vk_2():
    print("Инициализация сессий ВКонтакте (Бот 2)...")
    
    # 1. Создаем сессию для ЧТЕНИЯ донора
    try:
        vk_read_session = vk_api.VkApi(token=READ_TOKEN)
        vk_reader = vk_read_session.get_api()
        print("[Успех] Сессия для чтения исходной группы создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Не удалось создать сессию для чтения: {e}")
        return

    vk_sessions = {}
    
    # 2. Авторизуем каждую группу по её токену для ПУБЛИКАЦИИ
    for group_id, token in TARGET_GROUPS.items():
        try:
            vk_session = vk_api.VkApi(token=token)
            api = vk_session.get_api()
            # Проверяем токен группы. Обязательно передаем ID группы без минуса (abs)
            api.groups.getById(group_id=abs(group_id))
            vk_sessions[group_id] = api
            print(f"[Успех] Группа {group_id} авторизована.")
        except Exception as e:
            print(f"[Ошибка] Не удалось авторизовать группу {group_id}. Детали: {e}")

    if not vk_sessions:
        print("Ни одна целевая группа не авторизована. Скрипт остановлен.")
        return

    last_post_id = get_saved_last_post_id()
    
    # Твой кастомный сброс ID (оставил как было)
    if last_post_id == 481928: 
        last_post_id = 14991

    print(f"Бот 2 запущен. Готов к публикации в {len(vk_sessions)} групп(ы). Последний пост: {last_post_id}")

    while True:
        try:
            # Читаем стену донора через правильный READ_TOKEN
            response = vk_reader.wall.get(owner_id=SOURCE_GROUP_ID, count=2)
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
                print(f"[Бот 2] Найден новый пост: {current_post_id}.")
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
                
                # Публикуем во все группы через ИХ СОБСТВЕННЫЕ токены
                for target_id, vk_writer in vk_sessions.items():
                    try:
                        vk_writer.wall.post(
                            owner_id=target_id, 
                            from_group=1, 
                            message=post_text, 
                            attachments=attachments_str
                        )
                        print(f"[Бот 2] Пост успешно опубликован в {target_id}")
                        time.sleep(3)  # Пауза, чтобы ВК не заблокировал за спам
                    except Exception as e:
                        print(f"[Бот 2] Ошибка публикации в {target_id}: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)

        except Exception as e:
            print(f"[Бот 2] Ошибка получения постов: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    run_bot_vk_2()
