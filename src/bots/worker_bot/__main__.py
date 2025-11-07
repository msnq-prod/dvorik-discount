from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from bots.bot import worker_bot, worker_dp
from bots.api_client import api_client
from .states import RedeemCoupon, RecordPurchase

@worker_dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the Worker Bot! Use /redeem to start.")

@worker_dp.message(Command(commands=["redeem"]))
async def redeem_start(message: types.Message, state: FSMContext):
    await state.set_state(RedeemCoupon.waiting_for_code)
    await message.reply("Please enter the coupon code:")

@worker_dp.message(RedeemCoupon.waiting_for_code)
async def redeem_code_entered(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(RedeemCoupon.waiting_for_amount)
    await message.reply("Please enter the purchase amount:")

@worker_dp.message(RedeemCoupon.waiting_for_amount)
async def redeem_amount_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("code")
    amount = float(message.text)

    try:
        employee = await api_client.get(f"/employees/by-tg-id/{message.from_user.id}")
        coupon = await api_client.get(f"/coupons/by-code/{code}")
        client = await api_client.get(f"/clients/{coupon['client_id']}")

        response = await api_client.post(
            "/coupons/redeem",
            json={
                "code": code,
                "client_ref": client["identifier"],
                "amount": amount,
                "employee_id": employee["id"],
            },
        )
        await message.reply(
            f"Coupon redeemed successfully!\n"
            f"Amount: {response['amount']}\n"
            f"Discount: {response['discount']}\n"
            f"Payable: {response['payable']}"
        )
    except Exception as e:
        await message.reply(f"Failed to redeem coupon: {e}")
    finally:
        await state.clear()


@worker_dp.message(Command(commands=["purchase"]))
async def purchase_start(message: types.Message, state: FSMContext):
    await state.set_state(RecordPurchase.waiting_for_client_id)
    await message.reply("Please enter the client identifier (e.g., AB-123):")

@worker_dp.message(RecordPurchase.waiting_for_client_id)
async def purchase_client_id_entered(message: types.Message, state: FSMContext):
    await state.update_data(client_ref=message.text)
    await state.set_state(RecordPurchase.waiting_for_amount)
    await message.reply("Please enter the purchase amount:")

@worker_dp.message(RecordPurchase.waiting_for_amount)
async def purchase_amount_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client_ref = data.get("client_ref")
    amount = float(message.text)

    try:
        await api_client.post(
            "/purchases/",
            json={
                "client_ref": client_ref,
                "amount": amount,
                "employee_id": message.from_user.id,
            },
        )
        await message.reply("Purchase recorded successfully!")
    except Exception as e:
        await message.reply(f"Failed to record purchase: {e}")
    finally:
        await state.clear()


# This is a placeholder for running the bot with webhooks
async def main():
    # In a real application, you would set up a webhook here
    # For now, this will just confirm the bot is configured
    print("Worker bot configured and ready for webhooks.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
