from db.models import async_session
from db.models import User, Post
from sqlalchemy import select, func
import logging
from typing import Tuple, Dict, Optional
from sqlalchemy.exc import SQLAlchemyError

# Инициализация логгера
logger = logging.getLogger(__name__)

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)

async def search_user(
        user_id: int
    ) -> bool:
    '''
    Функция для проверки существования пользователя
    '''
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(
                select(User).where(User.user_id == user_id)
            )

            if not user:
                return False
            return True

async def add_user(
        user_id: int,
        username: str
    ) -> None:
    '''
    Функция для добавления пользователя
    '''
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(
                select(User).where(
                    User.user_id == user_id
                )
            )

            if not user:
                session.add(
                    User(
                        user_id=user_id,
                        username=username
                    )
                )
                logger.info(f"Пользователь {username} добавлен.")
            

async def add_post(
        user_id: int, 
        username: str, 
        message: str, 
        chat_id: int,
        channel: str
    ) -> bool:
    '''
    Функция для добавления поста.
    Вернёт False, если у пользователя уже есть пост.
    '''
    async with async_session() as session:
        async with session.begin():
            post = await session.scalar(select(Post).where(Post.user_id == user_id))

            if not post:  # Проверяем, что у пользователя нет поста
                session.add(
                    Post(
                        user_id=user_id,
                        username=username,
                        message=message,
                        chat_id=chat_id,
                        channel=channel
                    )
                )
                logger.info(f"Пост пользователя {username} добавлен в канал {channel}.")
                return True
            else:
                logger.info(f"У пользователя {username} уже есть пост.")
                return False

async def search_user_post(
        user_id: int
    ) -> bool:
    '''
    Функция для проверки существования постов у пользователя
    '''
    async with async_session() as session:
        async with session.begin():
            post = await session.scalar(
                select(Post).where(Post.user_id == user_id)
            )

            if not post:
                return False  # Нет постов у пользователя
            return True  # Есть посты у пользователя

async def first_post(channel_name: str) -> Tuple[bool, Optional[Dict[str, str]]]:
    """
    Функция для:
        - получения первого вопроса (post) из указанного канала,
        - отправки его в канал,
        - удаления вопроса (post).
    
    Args:
        channel_name (str): Название канала, из которого нужно получить первый пост.
    
    Returns:
        Tuple[bool, Optional[Dict[str, str]]]: 
        - bool: Успех операции.
        - dict: Словарь с информацией о посте (id, user_id, username, message, channel), если найден.
    """
    try:
        async with async_session() as session:  
            async with session.begin():
                # Получаем первый элемент из таблицы `Post` для указанного канала
                first_post = await session.execute(
                    select(Post)
                    .where(Post.channel == channel_name)
                    .order_by(Post.id)
                    .limit(1)
                )
                result = first_post.scalars().first()  # Извлекаем первый пост

                if result is None:
                    logger.info(f"Постов в канале '{channel_name}' нет.")
                    return False, None
                
                post = {
                    'id': result.id,
                    'user_id': result.user_id,
                    'username': result.username,
                    'message': result.message,
                    'chat_id': result.chat_id,
                    'channel': result.channel
                }
                logger.info(f"Сообщение с ID {result.message} получено из канала '{channel_name}'.")
                # Удаляем объект
                await session.delete(result)
                await session.commit()  # Подтверждаем изменения в базе данных
                logger.info(f"Сообщение с ID {result.id} из канала '{channel_name}' успешно удалено.")
                return True, post
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return False, None

async def count_posts(
        channel_name: str
    ) -> int:
    '''
    Функция для получения количества постов в определённом канале.
    '''
    async with async_session() as session:
        async with session.begin():            
            # Выполняем запрос, фильтруя по каналу и подсчитываем количество постов
            stmt = select(func.count(Post.id)).where(Post.channel == channel_name)  # Исправлено с 'channal' на 'channel'
            result = await session.execute(stmt)
            count = result.scalar()  # Получаем количество постов
            logger.info(f"Количество постов в канале {channel_name}: {count}")
            return count