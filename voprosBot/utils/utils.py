from aiogram.enums import ChatMemberStatus
from lexicon.ru import LEXICON_RU
from aiogram import Bot
import random, logging, requests

# Инициализация логгера
logger = logging.getLogger(__name__)

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)

#Проверяет подписку на канал
async def is_user_subscribed(bot: Bot, channel_url: str, telegram_id: int) -> bool:
    try:
        # Получаем username канала из URL
        channel_username = channel_url.split('/')[-1]
        
        # Получаем информацию о пользователе в канале
        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=telegram_id)

        # Проверяем статус пользователя
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False
    except Exception as e:
        # Если возникла ошибка (например, пользователь не найден или бот не имеет доступа к каналу)
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False

# Генерация простого математического примера
def generate_math_example():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    correct_answer = num1 + num2
    answers = []
    answers.append(correct_answer)
    l = [-2, -1, 1, 2]
    for i in range(4):
        answers.append(correct_answer + l[i])

    random.shuffle(answers)
    return f"{num1} + {num2} = ?", correct_answer, answers

def get_url_by_en(en_value):
    """
    Функция для получения URL канала по значению en.
    
    :param en_value: Строка, ключ en для поиска.
    :param channels: Список словарей с данными каналов.
    :return: URL канала или сообщение о том, что URL не найден.
    """
    for channel in LEXICON_RU['close_list']:
        if channel['en'] == en_value:
            return channel['url']
    return f"URL для en='{en_value}' не найден."

# Функция для отправки сообщений через URL
def send_post_via_url(en: str, token: str, message: str):
    channal = f'@{get_url_by_en(en).split("/")[-1]}'
    # URL для отправки сообщений через Telegram API
    BASE_URL = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": channal,
        "text": message,
        "parse_mode": "HTML",  # Можно использовать HTML или Markdown для форматирования
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 200:
            logging.info(f"Вопрос отправлен: \nКанал {channal}")
            return True, f"Вопрос отправлен: \nКанал {channal}"
        else:
            logging.error(f"Ошибка: {response.status_code} - {response.text}")
            return False, f"Ошибка: {response.status_code} - {response.text}"
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        return False, f"Ошибка при отправке сообщения: {e}"

# Шаблон для оформления поста в Telegram
def create_post_message(question: str, channel_name: str, username: str) -> str:
    """
    Функция для генерации сообщения для поста в Telegram канале.
    Публикуется вопрос с добавлением контекста.

    Args:
        question (str): Вопрос, который необходимо опубликовать.
        channel_name (str): Название канала, в который публикуется пост.
        username (str): Имя пользователя, который отправляет вопрос.

    Returns:
        str: Оформленное сообщение для публикации.
    """
    post_message = f"""
📝 **Вопрос на канале**: {channel_name}

👤 **От пользователя**: @{username}

💬 **Вопрос**:
{question}

-------------------------------------
✨ Если у вас есть вопросы, публикуйте их через нашего бота: [@VoprosNaDivanbot](https://t.me/VoprosNaDivanbot)
"""

    return post_message

# Шаблон для оформления поста в Telegram
def create_vip(question: str, channel_name: str, username: str) -> str:
    """
    Функция для генерации сообщения для поста в Telegram канале.
    Публикуется вопрос с добавлением контекста.

    Args:
        question (str): Вопрос, который необходимо опубликовать.
        channel_name (str): Название канала, в который публикуется пост.
        username (str): Имя пользователя, который отправляет вопрос.

    Returns:
        str: Оформленное сообщение для публикации.
    """
    print(username)
    if username == 'no':
        username = 'Аноним😶‍🌫️'
    post_message = f"""
     **💎VIP Вопрос на канале💎**: {channel_name}

👤 **От пользователя**: @{username}

💬 **Вопрос**:
{question}

-------------------------------------
✨ Если у вас есть вопросы, публикуйте их через нашего бота: [@VoprosNaDivanbot](https://t.me/VoprosNaDivanbot)
"""

    return post_message

def mes_user(channel: str):
    mes = f'''Ваш вопрос был опубликован на канле \n  {channel}'''
    return mes