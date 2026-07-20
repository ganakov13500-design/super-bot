import vk_api
import time
import os

# Настройки источника и интервала
SOURCE_GROUP_ID = -240374358  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id.txt'

# 1. ТОКЕН ДЛЯ ЧТЕНИЯ
READ_TOKEN = 'vk1.a.ezI_5MZF-3M53uwZ5z1uPr6Ge6xdFOgxVQ3ki0hfXO-NlpPkjPTR6Q_nNS_4uGHZtcAiKIxix_XC1hFqLjcQKcGH004RY86ZtJypWl872BK4cbF-BoLca2xU0RaeQkt82TJxAto9bJeWwwSp2Zl82ttitq9I1SeyRERKWfCCVCQdCQv_L-mYHrMG8Z9-d9F8IJEHWWWchiZ48XNMnIBsPw'

# 2. ТОКЕНЫ ДЛЯ ПУБЛИКАЦИИ
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
    print("Авторизация ВКонтакте (Бот 2)...")
    
    try:
        vk_read_session = vk_api.VkApi(token=READ_TOKEN)
        vk_reader = vk_read_session.get_api()
        print("[Успех] Сессия для чтения исходной группы создана.")
    except Exception as e:
        print(f"[Фатальная Ошибка] Не удалось создать сессию. Детали: {e}")
        return

    vk_sessions = {}
    for group_id, token in TARGET_GROUPS.items():
        try:
            vk_write_session = vk_api.VkApi(token=token)
            vk_writer = vk_write_session.get_api()
            vk_writer.groups.getById(group_id=abs(group_id)) 
            vk_sessions[group_id] = vk_writer
            print(f"[Успех] Целевая группа {group_id} авторизована.")
        except Exception as e:
            print(f"[Ошибка] Не удалось авторизовать группу {group_id}. Детали: {e}")

    if not vk_sessions:
        return

    last_post_id = get_saved_last_post_id()
    
    # ПРИНУДИТЕЛЬНЫЙ ЗАПУСК ДЛЯ ТЕСТА:
    # Раскомментируйте строку ниже (уберите решетку), чтобы заставить бота 
    # опубликовать текущий пост прямо сейчас в любом случае.
    # last_post_id = 1 

    print(f"Бот ВК 2 запущен. В памяти ID прошлого поста: {last_post_id}")

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

            # НОВАЯ СТРОКА ДЛЯ ДИАГНОСТИКИ:
            print(f"[Бот 2 ПРОВЕРКА] ID на стене: {current_post_id} | ID в памяти: {last_post_id}")

            if last_post_id == 0:
                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print(f"[Бот 2] Это ПЕРВЫЙ запуск. Запомнили пост {last_post_id}. Публиковать НЕ БУДЕМ. Ждем новый пост.")
            
            elif current_post_id <= last_post_id:
                print(f"[Бот 2] Новых постов нет (на стене {current_post_id} <= {last_post_id}). Ухожу в сон на 5 минут.")
                
            elif current_post_id > last_post_id:
                print(f"\n[Бот 2] НАЙДЕН НОВЫЙ ПОСТ: {current_post_id}! Начинаю рассылку...")
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
                
                for target_id, vk_writer in vk_sessions.items():
                    try:
                        vk_writer.wall.post(owner_id=target_id, from_group=1, message=post_text, attachments=attachments_str)
                        print(f"  -> Успешно отправлено в {target_id}")
                        time.sleep(3)
                    except Exception as e:
                        print(f"  -> Ошибка отправки в {target_id}: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)
                print("[Бот 2] Рассылка завершена. Возвращаюсь в режим ожидания.")

        except Exception as e:
            print(f"[Бот 2] Общая ошибка проверки постов: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    run_bot_vk_2()
    
