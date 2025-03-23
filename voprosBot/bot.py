import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config
# Импортируем роутеры
from handlers import other, user, admin, pay
# Импортируем миддлвари
#...
# Импортируем вспомогательные функции для создания нужных объектов
from keyboards.menu import set_main_menu
from db.models import async_main
from handlers.public import init_scheduler

# Инициализируем логгер
logger = logging.getLogger(__name__)

async def main():
    """
    Основная функция запуска Telegram-бота. 
    Настраивает логирование, загружает конфигурацию, 
    инициализирует объекты бота и диспетчера, регистрирует роутеры и миддлвари.
    """
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    # Загружаем конфигурацию
    config: Config = load_config()

    # Инициализация хранилища состояний
    storage = MemoryStorage()

    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Инициализация вспомогательных объектов (например, подключение к базе данных)
    await async_main()

    # Помещение объектов в workflow_data диспетчера
    dp.workflow_data.update({'BOT_TOKEN': config.tg_bot.token})

    # Настройка главного меню бота
    await set_main_menu(bot)

    # Регистрация роутеров
    logger.info('Подключаем роутеры')
    dp.include_router(admin.router)
    dp.include_router(pay.router)
    dp.include_router(user.router)
    dp.include_router(other.router)

    # Регистрация миддлвари
    logger.info('Подключаем миддлвари')
 
    #Публикация по расписанию
    init_scheduler(bot)

    # Пропуск накопившихся апдейтов и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    """ 
    Точка входа в приложение. Запускает функцию main с обработкой исключений.
    """
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
