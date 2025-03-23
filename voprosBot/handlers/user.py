import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from filters.filters import *
from fsm.fsm import *
from db.requests import *
from lexicon.ru import LEXICON_RU
from keyboards.keys import *
from utils.utils import *

# Создаем роутер
router = Router()

# Логгер
logger = logging.getLogger(__name__)

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    """
    Обработка команды /start.
    Отправляет пользователю приветственное сообщение и клавиатуру.
    """
    await message.answer(text=LEXICON_RU['start_mes'], reply_markup=start_key())


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands="help"))
async def process_help_command(message: Message):
    """
    Обработка команды /help.
    Отправляет пользователю текст помощи.
    """
    await message.answer(text=LEXICON_RU['help'])

# Этот хэндлер срабатывает на команду /paysupport
@router.message(Command(commands="paysupport"))
async def process_paysupport_command(message: Message):
    """
    Обработка команды /paysupport.
    Отправляет пользователю текст помощи.
    """
    await message.answer(text=LEXICON_RU['support'])

# Этот хэндлер срабатывает на команду /post
@router.message(Command(commands="post"), IsUser(), IsSub())
async def process_post_command(message: Message):
    """
    Обработка команды /post.
    Показывает пользователю, может ли он разместить пост.
    """
    if await search_user_post(message.from_user.id):
        await message.answer(
            LEXICON_RU['true_post'], 
            reply_markup=vip_key()
        )
    else:
        await message.answer(
            text=LEXICON_RU['post'],
            reply_markup=post_key()
        )

# Этот хэндлер срабатывает на команду /post
@router.message(Command(commands="post"))
async def process_post_command(message: Message):
    await message.answer(text=LEXICON_RU['post_f'])

# Этот хендлер срабатывает на нажатие на кнопку "Я подписался"
@router.callback_query(F.data == 'check_button')
async def process_check_press(callback: CallbackQuery, bot: Bot):
    """
    Обработка нажатия кнопки 'Проверка подписки'.
    Проверяет, подписан ли пользователь на все необходимые каналы.
    """
    try:
        for channel in LEXICON_RU['list']:
            label = channel['lable']
            url = channel['url']
            telegram_id = callback.from_user.id
            check = await is_user_subscribed(bot, url, telegram_id)
            if not check:
                await callback.message.answer(
                    f"{LEXICON_RU['no_sub']}{label}",
                    reply_markup=start_key()
                )
                return False

        sec = security_key()
        await callback.message.answer(
            text=f"{LEXICON_RU['bot_mes']}\n{sec[1]}",
            reply_markup=sec[0]
        )
    except Exception as e:
        logger.exception(f"Error in process_check_press: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


# Обработка нажатия на кнопки
@router.callback_query(F.data.startswith("math_answer"), StateFilter(default_state))
async def process_math_answer(callback: CallbackQuery, state: FSMContext):
    """
    Обработка ответа на математический вопрос для подтверждения безопасности.
    """
    try:
        res = callback.data.split(":")
        await state.clear()
        if int(res[1]) == int(res[2]):

            await add_user(callback.from_user.id, callback.from_user.username)
            is_vip = await search_user_post(callback.from_user.id)
            if is_vip:
                await callback.message.edit_text(
                    LEXICON_RU['true_post'], 
                    reply_markup=vip_key()
                )
            else:
                await callback.message.edit_text(
                    text=LEXICON_RU['security_true'],
                    reply_markup=post_key()
                )
        else:
            await callback.message.edit_text(LEXICON_RU['security_false'])
    except Exception as e:
        logger.exception(f"Error in process_math_answer: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")

# Обработка канала
@router.callback_query(F.data.startswith("channal"), StateFilter(FSMpost.fill_channal))
async def channal_input(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора канала для публикации поста.
    """
    try:
        res = callback.data.split(":")
        await state.update_data(channal=res[1])
        await state.set_state(FSMpost.fill_name)
        await callback.message.answer(text=LEXICON_RU['q_s'], reply_markup=anon_key())
    except Exception as e:
        logger.exception(f"Error in channal_input: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


# Обработка надо имя отображать или нет
@router.callback_query(F.data.startswith("name"), StateFilter(FSMpost.fill_name))
async def name_input(callback: CallbackQuery, state: FSMContext):
    res = callback.data.split("_")
    await state.update_data(anon=res[1])
    await state.set_state(FSMpost.fill_message)
    await callback.message.answer(text=LEXICON_RU['message_mes'])

# Обработка поста

@router.message(StateFilter(FSMpost.fill_message))
async def message_input(message: Message, state: FSMContext, BOT_TOKEN):
    """
    Обработка текста поста для отправки или сохранения.
    """
    await message.answer(text=LEXICON_RU['vop_true'])
    if IsCorrectPost():
        try:
            res = await state.get_data()

            if res['status'] == 'vip':
                channel = res['channal']
                mes = create_vip(message.text, channel, res['anon'])   
                await message.answer(send_post_via_url(channel, BOT_TOKEN, mes)[1])
                await state.clear()
                

            elif res['status'] == 'unvip':
                channel = res['channal']
                mes = message.text

                if res['anon'] == 'yes':
                    add = await add_post(
                        user_id=message.from_user.id,
                        username=message.from_user.username,
                        message=mes,
                        chat_id=message.chat.id,
                        channel=channel
                    )
                else:
                    add = await add_post(
                        user_id=message.from_user.id,
                        username='@Аноним😶‍🌫️',
                        message=mes,
                        chat_id=message.chat.id,
                        channel=channel
                    )
                if add:
                    await message.answer(
                        text=LEXICON_RU['use_vip'],
                    )
                    await state.clear()
                else:
                    await message.answer(text='Ошибка')
                    await state.clear()

        except Exception as e:
            logger.exception(f"Error in message_input: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")
    else:
        await message.answer(text=LEXICON_RU['false_mes'])
'''# Обработка поста
@router.message(StateFilter(FSMpost.fill_message))
async def message_input(message: Message):
    await message.answer(text=LEXICON_RU['false_mes'])'''

# Бесплатное размещение
@router.callback_query(F.data == 'free_button')
async def free_post_input(callback: CallbackQuery, state: FSMContext):
    """
    Обработка запроса на бесплатное размещение.
    """
    try:
        if await search_user_post(callback.from_user.id):
            await callback.message.answer(
                text=LEXICON_RU['true_post'],
                reply_markup=vip_key()
            )
            return
        await state.clear()
        await state.update_data(status='unvip')
        await state.set_state(FSMpost.fill_channal)
        await callback.message.answer(
            text=LEXICON_RU['get_channal'],
            reply_markup=channal_key()
        )
    except Exception as e:
        logger.exception(f"Error in free_post_input: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")
