import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus

# Replace with your Bot Token
BOT_TOKEN = "7381647603:AAFaCw2tIA4-OJA5j1iEYSNJGBrAnP0lCSo"

# Replace with your channel numeric ID & public username (if available)
REQUIRED_CHANNELS = {
    "-1002294570357": "Xstream_links2",
    "-1002337777714": "Sr_Robots"
}

API_URL = "https://text-to-speech.manzoor76b.workers.dev/?text={}&lang=hi"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_membership(user_id: int) -> bool:
    """Check if the user is a member of both required channels"""
    for channel_id, channel_username in REQUIRED_CHANNELS.items():
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            logger.info(f"Checking {user_id} in {channel_id}: {chat_member.status}")

            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.warning(f"User {user_id} is NOT a member of {channel_id}")
                return False
        except Exception as e:
            logger.error(f"Error checking membership for {user_id} in {channel_id}: {e}")
            return False
    return True

@dp.message(Command("start"))
async def start(message: Message):
    """Send a welcome message and check subscription"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = "🚀 To use this bot, please join both channels:\n"
        for channel_id, channel_username in REQUIRED_CHANNELS.items():
            join_message += f"🔹 [{channel_username}](https://t.me/{channel_username})\n"
        join_message += "After joining, send /start again!"
        
        await message.answer(join_message, parse_mode="Markdown")
        return

    await message.answer("✅ Welcome! Send me a text, and I'll convert it to speech in Hindi.")

@dp.message()
async def text_to_speech(message: Message):
    """Convert user text to speech using API and send the audio file"""
    user_id = message.from_user.id
    if not await check_membership(user_id):
        join_message = "🚀 To use this bot, please join both channels:\n"
        for channel_id, channel_username in REQUIRED_CHANNELS.items():
            join_message += f"🔹 [{channel_username}](https://t.me/{channel_username})\n"
        join_message += "After joining, send /start again!"

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
