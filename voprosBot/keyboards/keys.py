from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.utils import generate_math_example
from lexicon.ru import LEXICON_RU


def start_key():
    """
    Функция для создания стартовой клавиатуры с кнопками для подписки.
    """
    kb_list = LEXICON_RU['list']
    inline_keyboard = []

    for channel_data in kb_list:
        label = channel_data['lable']
        url = channel_data['url']

        # Добавление кнопки для каждого канала
        if label and url:
            inline_keyboard.append([InlineKeyboardButton(text=label, url=url)])

    # Добавление кнопки "Проверить подписку"
    inline_keyboard.append([InlineKeyboardButton(text=LEXICON_RU['check'], callback_data="check_button")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def security_key():
    """
    Функция для создания клавиатуры с кнопками для ответа на математическую задачу.
    """
    kb_builder = InlineKeyboardBuilder()

    # Генерация примера и возможных вариантов ответов
    question, correct_answer, answers = generate_math_example()

    # Добавление кнопок с вариантами ответов
    for answer in answers:
        kb_builder.add(
            InlineKeyboardButton(
                text=str(answer),
                callback_data=f"math_answer:{answer}:{correct_answer}"
            )
        )

    return kb_builder.as_markup(), question


def channal_key():
    """
    Функция для создания клавиатуры выбора канала.
    """
    kb_builder = InlineKeyboardBuilder()

    # Добавление кнопок для каждого канала из закрытого списка
    for channal in LEXICON_RU['close_list']:
        kb_builder.add(
            InlineKeyboardButton(
                text=channal['lable'],
                callback_data=f"channal:{channal['en']}"
            )
        )

    return kb_builder.as_markup()


def post_key():
    """
    Функция для создания клавиатуры с кнопками выбора режима публикации.
    """
    kb_builder = InlineKeyboardBuilder()
    
    # Кнопки для выбора режима публикации (VIP или FREE)
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['vip'], 
            callback_data='vip_button'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['free'], 
            callback_data='free_button'
        )
    )

    return kb_builder.as_markup()

def anon_key():
    """
    Функция для выбора режима публикации.
    """
    kb_builder = InlineKeyboardBuilder()
    
    # Кнопки для выбора режима публикации (VIP или FREE)
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['yes_ot'], 
            callback_data='name_yes'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['no_ot'], 
            callback_data='name_no'
        )
    )

    return kb_builder.as_markup()

def vip_key():
    """
    Функция для создания клавиатуры с кнопкой только VIP.
    """
    kb_builder = InlineKeyboardBuilder()

    # Кнопка для выбора VIP режима
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['vip'], 
            callback_data='vip_button'
        )
    )

    return kb_builder.as_markup()
