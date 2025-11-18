from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from bots.bot import client_bot, client_dp
from bots.api_client import api_client
from .states import RegisterClient

@client_dp.message(CommandStart())
async def send_welcome(message: types.Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("cmp_"):
        campaign_id = args[1].replace("cmp_", "")
        try:
            client = await api_client.get(f"/clients/by-tg-id/{message.from_user.id}")
            campaign = await api_client.get(f"/campaigns/{campaign_id}")
            await api_client.post(
                "/coupons/issue",
                json={
                    "client_ref": client["identifier"],
                    "campaign_id": int(campaign_id),
                    "template_id": campaign["template_id"],
                },
            )
            await message.reply("You have received a new coupon!")
        except Exception as e:
            await message.reply(f"Failed to get coupon: {e}")
    else:
        await message.reply("Welcome to the Loyalty Program! Use /register to start.")

@client_dp.message(Command(commands=["my_level"]))
async def my_level(message: types.Message):
    try:
        client = await api_client.get(f"/clients/by-tg-id/{message.from_user.id}")
        if client and client.get("level"):
            level_name = client["level"]["name"]
            total_spent = client["total_spent"]
            levels = await api_client.get("/levels/")
            next_level = None
            for level in sorted(levels, key=lambda x: x["threshold_amount"]):
                if level["threshold_amount"] > total_spent:
                    next_level = level
                    break

            progress_msg = ""
            if next_level:
                remaining = next_level["threshold_amount"] - total_spent
                progress_msg = f"\nProgress to next level: {remaining:.2f} RUB remaining."

            await message.reply(
                f"Your level is: {level_name}\n"
                f"Total spent: {total_spent:.2f} RUB{progress_msg}"
            )
        else:
            await message.reply("Could not retrieve your level information.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

@client_dp.message(Command(commands=["my_coupons"]))
async def my_coupons(message: types.Message):
    try:
        client = await api_client.get(f"/clients/by-tg-id/{message.from_user.id}")
        if client:
            coupons = await api_client.get(f"/clients/{client['id']}/coupons")
            if coupons:
                coupon_list = "\n".join(
                    [
                        f"- `{coupon['code']}` (expires: {coupon.get('expires_at', 'N/A')})"
                        for coupon in coupons
                        if coupon["status"] == "issued"
                    ]
                )
                await message.reply(f"Your active coupons:\n{coupon_list}")
            else:
                await message.reply("You have no active coupons.")
        else:
            await message.reply("Could not retrieve your information.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")


@client_dp.message(Command(commands=["register"]))
async def register_start(message: types.Message, state: FSMContext):
    await state.set_state(RegisterClient.waiting_for_first_name)
    await message.reply("Please enter your first name:")

@client_dp.message(RegisterClient.waiting_for_first_name)
async def first_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(RegisterClient.waiting_for_last_name)
    await message.reply("Please enter your last name:")

@client_dp.message(RegisterClient.waiting_for_last_name)
async def last_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(RegisterClient.waiting_for_birth_date)
    await message.reply("Please enter your birth date (YYYY-MM-DD):")

@client_dp.message(RegisterClient.waiting_for_birth_date)
async def birth_date_entered(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await state.set_state(RegisterClient.waiting_for_gender)
    await message.reply("Please enter your gender (male, female, other):")

@client_dp.message(RegisterClient.waiting_for_gender)
async def gender_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await api_client.post(
            "/clients/",
            json={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "birth_date": data["birth_date"],
                "gender": message.text,
                "tg_id": message.from_user.id,
            },
        )
        await message.reply("You have been successfully registered!")
    except Exception as e:
        await message.reply(f"Registration failed: {e}")
    finally:
        await state.clear()


# This is a placeholder for running the bot with webhooks
async def main():
    # In a real application, you would set up a webhook here
    # For now, this will just confirm the bot is configured
    print("Client bot configured and ready for webhooks.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
