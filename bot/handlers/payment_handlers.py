from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from bot.services.payments import add_generations_to_user_balance


router = Router()

@router.message(F.text == "⭐️ Купить генерации")
@router.message(F.text == "/buy")
async def buy_generations_cmd(message: Message):
    prices = [LabeledPrice(label="10 генераций NanoBanana", amount=50)]
    
    await message.answer_invoice(
        title="Пополнение баланса",
        description="Пакет из 10 генераций изображений через нейросеть.",
        payload="buy_10_attempts_payload",
        currency="XTR",
        provider_token="",
        prices=prices
    )

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    
    if payment_info.invoice_payload == "buy_10_attempts_payload":
        user_id = message.from_user.id
        attempts_to_add = 10
        
        success = await add_generations_to_user_balance(user_id, attempts_to_add)
        
        if success:
            await message.answer(
                f"🎉 Спасибо за покупку!\n\n"
                f"Вам успешно начислено {attempts_to_add} генераций. Можете приступать к созданию аватарок!"
            )
        else:
            await message.answer(
                "❌ Произошла техническая ошибка при зачислении попыток.\n"
                "Пожалуйста, свяжитесь с администратором, предоставив скриншот этого сообщения и чек оплаты."
            )