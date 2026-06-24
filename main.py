import multiprocessing
import time
import os
from aiohttp import web

# Импортируем функции запуска из файлов ботов
from bot_vk_1 import run_bot_vk_1
from bot_vk_2 import run_bot_vk_2
from bot_mail import run_bot_mail
from bot_max import run_bot_max

# ==========================================
#     ВЕБ-СЕРВЕР ДЛЯ ЗАЩИТЫ ОТ СНА НА RENDER
# ==========================================
async def handle_ping(request):
    return web.Response(text="Супер-Бот (4 в 1) работает стабильно!")

def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    port = int(os.environ.get("PORT", 10000))
    print(f"[SERVER] Веб-сервер запущен на порту {port}")
    web.run_app(app, host='0.0.0.0', port=port, access_log=None)

# ==========================================
#               ГЛАВНЫЙ ЗАПУСК
# ==========================================
if __name__ == '__main__':
    print("[SYSTEM] Инициализация всех модулей...")

    # Список ботов для параллельного запуска
    bot_functions = [
        run_bot_vk_1,
        run_bot_vk_2,
        run_bot_mail,
        run_bot_max
    ]
    
    processes = []
    
    # 1. Запускаем каждого бота в отдельном процессе
    for func in bot_functions:
        process = multiprocessing.Process(target=func)
        process.start()
        processes.append(process)
        print(f"[SYSTEM] Процесс запущен: {func.__name__}")
        time.sleep(2) # Пауза, чтобы не нагружать CPU при старте
        
    # 2. Запускаем веб-сервер в главном процессе (он держит Render активным)
    try:
        run_web_server()
    except KeyboardInterrupt:
        print("[SYSTEM] Остановка сервера. Завершение работы процессов...")
        for process in processes:
            process.terminate()
            process.join()
        print("[SYSTEM] Работа завершена.")
