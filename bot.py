import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# Replace with your Bot Token
BOT_TOKEN = "7381647603:AAFaCw2tIA4-OJA5j1iEYSNJGBrAnP0lCSo"

# Replace with your required channel usernames (without @)
REQUIRED_CHANNELS = ["Xstreamlinks2", "Sr_Robots"]

API_URL = "https://text-to-speech.manzoor76b.workers.dev/?text={}&lang=hi"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def check_membership(user_id: int) -> bool:
    """Check if the user is a member of both required channels"""
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await bot.get_chat_member(f"@{channel}", user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=["start"])
async def start(message: Message):
    """Send a welcome message and check subscription"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = (
            f"🚀 To use this bot, please join both channels:\n"
            f"1️⃣ [YourChannel1](https://t.me/{REQUIRED_CHANNELS[0]})\n"
            f"2️⃣ [YourChannel2](https://t.me/{REQUIRED_CHANNELS[1]})\n"
            f"After joining, send /start again!"
        )
        await message.reply(join_message, parse_mode="Markdown")
        return

    await message.reply("✅ Welcome! Send me a text, and I'll convert it to speech in Hindi.")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def text_to_speech(message: Message):
    """Convert user text to speech using API and send the audio file"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = (
            f"🚀 To use this bot, please join both channels:\n"
            f"1️⃣ [YourChannel1](https://t.me/{REQUIRED_CHANNELS[0]})\n"
            f"2️⃣ [YourChannel2](https://t.me/{REQUIRED_CHANNELS[1]})\n"
            f"After joining, send /start again!"
        )
        await message.reply(join_message, parse_mode="Markdown")
        return

    user_text = message.text.strip()
    
    if not user_text:
        await message.reply("⚠️ Please provide some text to convert to speech.")
        return

    api_endpoint = API_URL.format(user_text)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_endpoint) as response:
            if response.status == 200:
                audio_file = "output.mp3"
                with open(audio_file, "wb") as file:
                    file.write(await response.read())

                with open(audio_file, "rb") as audio:
                    await bot.send_voice(message.chat.id, audio)

                os.remove(audio_file)
            else:
                await message.reply("⚠️ Failed to generate speech. Please try again.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
