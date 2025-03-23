from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from filters.filters import IsAdmin
from aiogram.exceptions import TelegramBadRequest

from lexicon.ru import LEXICON_RU
# Создаем роутер
router = Router()

# Обработка возврата средств (если возможно через провайдера)
@router.message(Command("refund"), IsAdmin())
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
):
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(
            LEXICON_RU['support']
        )
        return
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            LEXICON_RU['good']
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = LEXICON_RU['no_found']
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = LEXICON_RU['already']
        else:
            # При всех остальных ошибках – такой же текст,
            # как и в первом случае
            text = LEXICON_RU['no_found']
        await message.answer(text)
        return