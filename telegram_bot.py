import asyncio
import json
import logging
import time

from aiogram import Bot, Dispatcher

import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Конфігурація
class Config:
    BOT_TOKEN = settings.telegram_bot_id
    LOG_FILE_PATH = 'logs/log.log'
    TARGET_CHAT_ID = settings.chat_id
    SENT_LOGS_FILE = 'logs/sent_logs.json'


def format_log_message(log):
    """Форматування логу з емодзі та структурою"""
    # Визначення типу логу та відповідного емодзі
    emoji_map = {
        'error': '🚨',
        'critical': '💥',
        'warning': '⚠️',
        'info': '📝',
        'debug': '🔍'
    }

    # Пошук типу логу
    log_type = 'info'
    for key, emoji in emoji_map.items():
        if key in log.lower():
            log_type = key
            break

    # Форматування повідомлення
    formatted_message = f"""
{emoji_map.get(log_type, '📌')} <b>{log_type.upper()} Log</b>

📅 Деталі:
<code>{log}</code>

🕒 Час реєстрації: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return formatted_message


def load_sent_logs():
    """Завантаження списку надісланих логів"""
    try:
        with open(Config.SENT_LOGS_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_sent_logs(sent_logs):
    """Збереження списку надісланих логів"""
    with open(Config.SENT_LOGS_FILE, 'w') as f:
        json.dump(list(sent_logs), f)


async def parse_log_file(sent_logs):
    """Парсинг нових логів"""
    try:
        with open(Config.LOG_FILE_PATH, 'r') as file:
            logs = file.readlines()

        # Фільтрація логів, які ще не надсилали
        new_logs = [
            log.strip() for log in logs
            if log.strip() not in sent_logs
        ]

        return new_logs
    except Exception as e:
        logger.error(f"Помилка читання файлу: {e}")
        return []


async def send_logs_to_telegram(bot, logs, chat_id, sent_logs):
    """Надсилання логів у Telegram"""
    if not logs:
        return sent_logs

    # Надсилання кожного логу окремим повідомленням
    for log in logs:
        try:
            formatted_log = format_log_message(log)
            await bot.send_message(
                chat_id,
                formatted_log,
                parse_mode='HTML'
            )
            sent_logs.add(log)
            # Невелика затримка між повідомленнями
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Помилка надсилання логу: {e}")

    return sent_logs


async def log_monitoring_job(bot):
    """Моніторинг логів"""
    sent_logs = load_sent_logs()

    while True:
        await asyncio.sleep(60)  # Перевірка кожну хвилину

        try:
            logs = await parse_log_file(sent_logs)

            if logs:
                sent_logs = await send_logs_to_telegram(
                    bot,
                    logs,
                    Config.TARGET_CHAT_ID,
                    sent_logs
                )

                # Збереження оновленого списку надісланих логів
                save_sent_logs(sent_logs)

        except Exception as e:
            logger.error(f"Помилка моніторингу: {e}")


async def parsing():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    # Запуск моніторингу логів
    asyncio.create_task(log_monitoring_job(bot))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Помилка роботи бота: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(parsing())