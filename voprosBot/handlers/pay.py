from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from lexicon.ru import LEXICON_RU
from keyboards.keys import channal_key
from utils.utils import send_post_via_url
from fsm.fsm import FSMpost

# Создаем роутер
router = Router()

# Обработка запроса на предоплату
@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    # Проверка на валидность данных перед подтверждением платежа
    # Если все ок, отправляем ответ
    await pre_checkout_query.answer(ok=True)


# Кнопка для оформления VIP-оплаты
@router.callback_query(F.data == 'vip_button')
async def cmd_donate(callback_query: CallbackQuery, bot: Bot):
    # Создаем объект цен
    prices = [LabeledPrice(label="XTR", amount=LEXICON_RU['amount'])]

    # Отправляем инвойс через Telegram-бота
    await bot.send_invoice(
        chat_id=callback_query.message.chat.id,
        title=LEXICON_RU['pay_title'],
        description=LEXICON_RU['pay_info'],
        payload=f"{LEXICON_RU['amount']}_stars",  # Уникальная строка для отслеживания
        provider_token="YOUR_PROVIDER_TOKEN",  # Замените на реальный токен вашего провайдера
        currency="XTR",  # Используем валюту Stars (или другую валюту, если используется)
        prices=prices,  # Установим цену
        start_parameter="vip-payment",  # Параметр для стартовой страницы
    )

    # Уведомление для пользователя, что инвойс отправлен
    await callback_query.answer("Счет на оплату отправлен. Проверьте сообщения в чате.")


# Обработка успешной оплаты
@router.message(F.successful_payment, StateFilter(default_state))
async def on_successful_payment(message: Message, state: FSMContext):
    # Сообщение об успешной оплате и переход к выбору канала
    await message.answer(
        text=LEXICON_RU['get_channal'],
        reply_markup=channal_key()
    )
    # Очистка состояния и установка состояния для дальнейшей работы
    await state.clear()
    await state.update_data(status='vip')  # Статус пользователя изменен на VIP
    await state.set_state(FSMpost.fill_channal)  # Переход к следующему состоянию


