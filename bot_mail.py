import imaplib
import email
from email.header import decode_header
import time
import requests
import asyncio

EMAIL_LOGIN = 'sharoy-roo@mail.ru'
EMAIL_PASSWORD = 'nJ4r4YVkd1fA5mOrhw5Z'
IMAP_SERVER = 'imap.mail.ru'
ID_INSTANCE = '7107631855'
API_TOKEN = '6b85d9d9086b4c18919ab1d919c3795d896e40cfb1244c42a8'
WHATSAPP_CHAT_ID = '120363423933263919@g.us'
CHECK_INTERVAL = 60  

def decode_mime_words(s):
    if not s: return "(Без заголовка)"
    decoded_words = []
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            charset = encoding if encoding else 'utf-8'
            try: decoded_words.append(word.decode(charset))
            except: decoded_words.append(word.decode('windows-1251', errors='ignore'))
        else:
            decoded_words.append(word)
    return u''.join(decoded_words)

def send_whatsapp_message(text):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    try: requests.post(url, json={"chatId": WHATSAPP_CHAT_ID, "message": text})
    except Exception as e: print(f"[Бот Mail] Ошибка WhatsApp: {e}")

async def check_mail_loop():
    print("Запуск бота Mail.ru...")
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
            mail.select("INBOX")
            status, messages = mail.search(None, "UNSEEN")
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                for e_id in email_ids:
                    res, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject = decode_mime_words(msg.get("Subject"))
                            sender = decode_mime_words(msg.get("From"))
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try: body = part.get_payload(decode=True).decode(); break
                                        except: pass
                            else:
                                try: body = msg.get_payload(decode=True).decode()
                                except: pass
                            
                            if len(body) > 500: body = body[:500] + "\n[...]"
                            text = f"📧 *НОВОЕ ПИСЬМО (Mail.ru)*\n👤 *От:* {sender}\n📌 *Тема:* {subject}\n📝 *Текст:*\n{body.strip()}"
                            send_whatsapp_message(text)
                            await asyncio.sleep(2) 
            mail.logout()
        except Exception as e: print(f"[Бот Mail] Ошибка: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

def run_bot_mail():
    asyncio.run(check_mail_loop())
