from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import Bot
from db.requests import search_user
from filters.check import check_text
from config import Config, load_config
from lexicon.ru import LEXICON_RU
from utils.utils import is_user_subscribed
import logging

# Инициализация логгера
logger = logging.getLogger(__name__)

config: Config = load_config()

class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        self.admin_ids = config.tg_bot.admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


class IsCorrectPost(BaseFilter):
    """
    Фильтр для проверки корректности текста поста.
    Возвращает True, если текст проходит проверку, иначе False.
    """
    async def __call__(self, message: Message) -> bool:
        try:
            is_correct = check_text(message.text)
            logger.info(f"Проверка текста поста: {message.text} - {'корректный' if is_correct else 'некорректный'}")
            return is_correct
        except Exception as e:
            logger.error(f"Ошибка при проверке текста поста: {e}")
            return False

class IsUser(BaseFilter):
    """
    Фильтр для проверки существования пользователя в базе данных.
    Возвращает True, если пользователь существует, иначе False.
    """
    async def __call__(self, message: Message) -> bool:
        try:
            user_exists = await search_user(message.from_user.id)
            logger.info(f"Проверка существования пользователя {message.from_user.id}: {'найден' if user_exists else 'не найден'}")
            return user_exists
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя {message.from_user.id}: {e}")
            return False
        
class IsSub(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        for channel in LEXICON_RU['list']:
            url = channel['url']
            telegram_id = message.from_user.id
            check = await is_user_subscribed(bot, url, telegram_id)
            if not check:
                return False
        return True