from aiogram import types
from aiogram.filters import CommandStart, Command
from bots.bot import client_bot, client_dp
from bots.api_client import api_client

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
        await message.reply("Welcome to the Loyalty Program!")

@client_dp.message(Command(commands=["my_level"]))
async def my_level(message: types.Message):
    # Placeholder
    await message.reply("Your level is: Bronze")

@client_dp.message(Command(commands=["my_coupons"]))
async def my_coupons(message: types.Message):
    # Placeholder
    await message.reply("Your coupons are: ...")

# This is a placeholder for running the bot with webhooks
async def main():
    # In a real application, you would set up a webhook here
    # For now, this will just confirm the bot is configured
    print("Client bot configured and ready for webhooks.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
