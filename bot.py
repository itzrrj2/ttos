import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus

# Replace with your Bot Token
BOT_TOKEN = "7381647603:AAFaCw2tIA4-OJA5j1iEYSNJGBrAnP0lCSo"

# Replace with your required channel numeric IDs (or usernames if public)
REQUIRED_CHANNELS = ["-1002294570357", "-1002337777714"]

API_URL = "https://text-to-speech.manzoor76b.workers.dev/?text={}&lang=hi"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_membership(user_id: int) -> bool:
    """Check if the user is a member of both required channels"""
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await bot.get_chat_member(channel, user_id)
            logger.info(f"Checking {user_id} in {channel}: {chat_member.status}")

            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False
        except Exception as e:
            logger.error(f"Error checking membership for {user_id} in {channel}: {e}")
            return False
    return True

@dp.message(Command("start"))
async def start(message: Message):
    """Send a welcome message and check subscription"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = (
            f"🚀 To use this bot, please join both channels:\n"
            f"1️⃣ [Channel 1](https://t.me/{REQUIRED_CHANNELS[0]})\n"
            f"2️⃣ [Channel 2](https://t.me/{REQUIRED_CHANNELS[1]})\n"
            f"After joining, send /start again!"
        )
        await message.answer(join_message, parse_mode="Markdown")
        return

    await message.answer("✅ Welcome! Send me a text, and I'll convert it to speech in Hindi.")

@dp.message()
async def text_to_speech(message: Message):
    """Convert user text to speech using API and send the audio file"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = (
            f"🚀 To use this bot, please join both channels:\n"
            f"1️⃣ [Channel 1](https://t.me/{REQUIRED_CHANNELS[0]})\n"
            f"2️⃣ [Channel 2](https://t.me/{REQUIRED_CHANNELS[1]})\n"
            f"After joining, send /start again!"
        )
        await message.answer(join_message, parse_mode="Markdown")
        return

    user_text = message.text.strip()
    
    if not user_text:
        await message.answer("⚠️ Please provide some text to convert to speech.")
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
                await message.answer("⚠️ Failed to generate speech. Please try again.")

async def main():
    """Start the bot"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
