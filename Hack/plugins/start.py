import env
from Hack import bot
from Hack.helpers import MENU1, KEYBOARD1
from Hack.database import DB
from telethon import events
from telethon.tl.custom.button import Button

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    id = event.sender_id
    photo = env.START_IMG_URL
    mention = f"[{event.sender.first_name}](tg://user?id={id})"
    TEXT = "Hey {}, I am a Session Hack Bot Supporting Both Pyrogram and Telethon Session String. Type /hack to see the menu"
    updates_url = "https://t.me/TheChampu"
    support_url = "https://t.me/FenuZone"
    owner_url = "https://t.me/itsMeShivanshu"
    chat_url = "https://t.me/TheChampuClub"
    help_button = Button.inline("ʜᴀᴄᴋ 📲", data="help_callback")

    buttons = [
        [
            Button.url("ᴜᴘᴅᴀᴛᴇꜱ ⚡️", url=updates_url),
            Button.url("💬 ꜱᴜᴘᴘᴏʀᴛ", url=support_url)
        ],
        [
            Button.url("ᴄʜᴀᴛ ɢʀᴏᴜᴘ 💌", url=chat_url),
            Button.url("💕 ᴏᴡɴᴇʀ", url=owner_url)
        ],
        [help_button],
    ]

    # Send the message with buttons
    await event.reply(TEXT.format(mention), buttons=buttons)

    if DB:
        await DB.add_user(id)
    if env.LOG_GROUP_ID:
        await bot.send_message(env.LOG_GROUP_ID, f'{mention} Has Just Started The Bot')

@bot.on(events.CallbackQuery(data="help_callback"))
async def help_callback_handler(event):
    # Trigger the /help command
    await hack(event)
    
@bot.on(events.CallbackQuery(data="back_callback"))
async def back_callback_handler(event):
    # Trigger the /help command
    await start(event)
    
@bot.on(events.NewMessage(pattern="/hack"))
async def hack(event):
    if not event.is_private:
        return await event.reply("You can't use me in groups.")
    await event.reply(MENU1, buttons=KEYBOARD1)