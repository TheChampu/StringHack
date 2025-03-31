import base64
import struct
import asyncio
import ipaddress
import requests as r

from Hack import bot
from logger import LOGGER
from traceback import format_exc
from env import LOG_GROUP_ID, MUST_JOIN, DISABLED

from telethon import errors, Button
from telethon.events import CallbackQuery
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession
from telethon.errors.rpcerrorlist import UserNotParticipantError, UserIsBlockedError


MENU1 = '''
ᴀ - ᴄʜᴇᴄᴋ ᴜsᴇʀ ᴏᴡɴ ɢʀᴏᴜᴘs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs(ᴘᴜʙʟɪᴄ ᴏɴʟʏ)

ʙ - ᴄʜᴇᴄᴋ ᴜsᴇʀ ᴀʟʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ʟɪᴋᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ, ᴜsʀɴᴀᴍᴇ... ᴇᴛᴄ

ᴄ - ʙᴀɴ ᴀʟʟ ᴛʜᴇ ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ

ᴅ - ᴋɴᴏᴡ ᴜsᴇʀ ʟᴀsᴛ ᴏᴛᴘ, ᴜsᴇ ᴏᴘᴛɪᴏɴ ʙ ғɪʀsᴛ ᴛᴏ ᴛᴀᴋᴇ ɴᴜᴍʙᴇʀ ᴛʜᴇɴ ʟᴏɢɪɴ

ᴇ - ᴊᴏɪɴ ᴀ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ/ʟɪɴᴋ ᴠɪᴀ sᴛʀɪɴɢsᴇssɪᴏɴ

ғ - ʟᴇᴀᴠᴇ ᴀ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ ᴠɪᴀ sᴛʀɪɴɢsᴇssɪᴏɴ

ɢ - ᴅᴇʟᴇᴛᴇ ᴀ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ

ʜ - ᴄʜᴇᴄᴋ ᴜsᴇʀ ᴛᴡᴏ sᴛᴇᴘ ɪs ᴇɴᴇᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ
'''

MENU2 = '''
ɪ - ᴛᴇʀᴍɪɴᴀᴛᴇ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴs ᴇxᴄᴇᴘᴛ ʏᴏᴜʀ sᴛʀɪɴɢsᴇssɪᴏɴ

ᴊ - ᴅᴇʟᴇᴛᴇ ᴀᴄᴄᴏᴜɴᴛ

ᴋ - ʟᴇᴀᴠᴇ ᴀʟʟ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs

ʟ - ʙʀᴏᴀᴅᴄᴀsᴛ ʙᴜᴛᴛᴏɴs

ᴍ - ᴛᴇʀᴍɪɴᴀᴛᴇ ᴄᴜʀʀᴇɴᴛ sᴇssɪᴏɴ

ɴ - ɪɴᴠɪᴛᴇ ᴀʟʟ

ᴏ - ᴅᴇᴍᴏᴛᴇ ᴀ ᴍᴇᴍʙᴇʀ

ᴘ - ᴘʀᴏᴍᴏᴛᴇ ᴀ ᴍᴇᴍʙᴇʀ
'''

BROADCAST_BUTTONS = [[
    Button.inline("Group", data="1"),
    Button.inline("User", data="2"),
], [
    Button.inline("All", data="3"),
]]

BROADCAST_OPTION = {
    b"1": {
        "group": True
    },
    b"2": {
        "user": True
    },
    b"3": {
        "group": True,
        "user": True
    }
}

KEYBOARD1 = [
    [
        Button.inline("A", data="A"),
        Button.inline("B", data="B"),
        Button.inline("C", data="C"),
        Button.inline("D", data="D")
    ],
    [
        Button.inline("E", data="E"),
        Button.inline("F", data="F"),
        Button.inline("G", data="G"),
        Button.inline("H", data="H")
    ],
    [
        Button.inline("Next ⏭️", data="next")
    ],
    [
        Button.inline("ʜᴏᴍᴇ 🏘", data="back_callback")
    ],
]

KEYBOARD2 = [
    [
        Button.inline("I", data="I"),
        Button.inline("J", data="J"),
        Button.inline("K", data="K"),
        Button.inline("L", data="L")
    ],
    [
        Button.inline("M", data="M"),
        Button.inline("N", data="N"),
        Button.inline("O", data="O"),
        Button.inline("P", data="P")
    ],
    [
        Button.inline("back ⏮️", data="back")
    ],
    [
        Button.inline("ʜᴏᴍᴇ 🏘", data="back_callback")
    ],
]


async def join_checker(e):
    if not MUST_JOIN:
        return True
    chat = await bot.get_entity(MUST_JOIN)
    try:
        await bot(GetParticipantRequest(chat, e.sender_id))
        return True
    except UserNotParticipantError:
        join_chat = f"https://t.me/{chat.username}"
        button = [[
            Button.url(text="Join", url=join_chat),
        ]]

        TEXT = "Hey looks like you haven't join our chat yet, Please join first!"

        await bot.send_message(e.sender_id, TEXT, buttons=button)

        return False
    except Exception as err:
        LOGGER(__name__).error(err)
        return True


def paste(text):
    link = 'https://spaceb.in/'
    url = 'https://spaceb.in/api/v1/documents'
    payload = {"content": text, "extension": "txt"}
    headers = {
        "Content-Type": "application/json"
    }

    response = r.post(url, json=payload, headers=headers)
    hash = response.json().get('payload').get('id')

    return link + hash


def on_callback(data=None):
    def dec(func):
        async def wrap(e):
            check = await join_checker(e)
            if not check:
                return

            if func.__name__ in DISABLED:
                await e.answer("This function is currently disabled", alert=True)
                return
            try:
                await func(e)
            except errors.common.AlreadyInConversationError:
                pass
            except (asyncio.CancelledError, UserIsBlockedError):
                return
            except Exception as err:
                ERROR_TXT = f'ERROR MESSAGE:- {err}'
                ERROR_TXT += f'\n\nERROR TRACEBACK:- {format_exc()}'
                if LOG_GROUP_ID:
                    try:
                        link = paste(ERROR_TXT)
                        await bot.send_message(LOG_GROUP_ID, link, link_preview=False)
                    except:
                        pass
                else:
                    LOGGER(__name__).error(ERROR_TXT)
                await e.reply('Some Error occur from bot side. Please report it to @TheChampu')

        bot.add_event_handler(wrap, CallbackQuery(data=data))

    return dec


_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def validate_session(session):
    # Telethon Session
    if session.startswith(CURRENT_VERSION):
        if len(session.strip()) != 353:
            return False
        return StringSession(session)

    # Pyrogram Session
    elif len(session) in _PYRO_FORM.keys():
        if len(session) in [351, 356]:
            dc_id, _, auth_key, _, _ = struct.unpack(
                _PYRO_FORM[len(session)],
                base64.urlsafe_b64decode(session + "=" *
                                         (-len(session) % 4)),
            )
        else:
            dc_id, _, _, auth_key, _, _ = struct.unpack(
                _PYRO_FORM[len(session)],
                base64.urlsafe_b64decode(session + "=" *
                                         (-len(session) % 4)),
            )
        return StringSession(CURRENT_VERSION + base64.urlsafe_b64encode(
            struct.pack(
                _STRUCT_PREFORMAT.format(4),
                dc_id,
                ipaddress.ip_address(DC_IPV4[dc_id]).packed,
                443,
                auth_key,
            )).decode("ascii"))
    else:
        return False