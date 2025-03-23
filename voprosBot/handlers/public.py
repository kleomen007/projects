import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Router, Bot
from lexicon.ru import LEXICON_RU
from db.requests import first_post
from utils.utils import create_post_message, mes_user

logger = logging.getLogger(__name__)

# Функция для отправки сообщений
async def send_post(bot: Bot):
    for channal in LEXICON_RU['close_list']:
        post = await first_post(channal['en'])
        url = mes_user(channal['url'])
        if post[0]:
            mes = create_post_message(post[1]['message'], post[1]['channel'], post[1]['username'])
            try:
                await bot.send_message(chat_id=channal['chat_id'], text=f'{mes}')
                logging.info(f"Сообщение отправлено: {post[1]['message']}\nКанал {channal['en']}")
                await bot.send_message(chat_id=post[1]['chat_id'], text=f'{url}')
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения: {e}")

# Функция для инициализации планировщика
def init_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Добавляем задачи в планировщик
    for hour in range(9, 23):  # С 9:00 до 22:00
        scheduler.add_job(send_post, "cron", hour=hour, minute="0", kwargs={"bot": bot})

    # Запускаем планировщик
    scheduler.start()
    logger.info("Планировщик задач успешно запущен")

    return scheduler
