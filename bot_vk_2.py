import vk_api
import time
import os

TOKEN = 'vk1.a.1nUfskY4yfVR5NONEfxscxFqYhpSpd8CBGB7L528bPbOnvz8nVZUzE7Yv1PHJyUFzEllvSSSA8QvSXF5Lpd7mZKfQxa5RFc7JB_1caCb700QoIiDEPB19VzMm3BEkeCfm1Xi4ECsYfhXB1aSPMJ-U_mGbr4nmxfGSbTIQeHPzwVMGMEBChSL3Gq3sLxw0-1Bj93cnVFqFfl1zsBkU8IDEA'
SOURCE_GROUP_ID = -204081884  
TARGET_GROUP_IDS = [-215578086, -221202163, -219647526, -219649455, -215622579]  
CHECK_INTERVAL = 300  
LAST_POST_FILE = 'last_post_id.txt'

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
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        vk.users.get() 
    except Exception as e:
        print(f"Ошибка авторизации (Бот 2): {e}")
        return

    last_post_id = get_saved_last_post_id()
    if last_post_id == 481928: last_post_id = 14991

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
                print(f"[Бот 2] Найден новый пост: {current_post_id}.")
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
                        vk.wall.post(owner_id=target_id, from_group=1, message=post_text, attachments=attachments_str)
                        time.sleep(3)  
                    except Exception as e:
                        print(f"[Бот 2] Ошибка публикации: {e}")

                last_post_id = current_post_id
                save_last_post_id(last_post_id)
        except Exception as e:
            print(f"[Бот 2] Ошибка: {e}")
        time.sleep(CHECK_INTERVAL)
