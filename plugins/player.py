# Aditya Halder // @AdityaHalder

import os
import aiofiles
import aiohttp
import ffmpeg
import requests
from os import path
from asyncio.queues import QueueEmpty
from typing import Callable
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from modules.cache.admins import set
from modules.clientbot import clientbot, queues
from modules.clientbot.clientbot import client as USER
from modules.helpers.admins import get_administrators
from youtube_search import YoutubeSearch
from modules import converter
from modules.downloaders import youtube
from modules.config import DURATION_LIMIT, que, SUDO_USERS
from modules.cache.admins import admins as a
from modules.helpers.filters import command, other_filters
from modules.helpers.command import commandpro
from modules.helpers.decorators import errors, authorized_users_only
from modules.helpers.errors import DurationLimitError
from modules.helpers.gets import get_url, get_file_name
from PIL import Image, ImageFont, ImageDraw
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

# plus
chat_id = None
useer = "NaN"


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("resource/thumbnail.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("resource/font.otf", 32)
    draw.text((190, 550), f"Title: {title[:50]} ...", (255, 255, 255), font=font)
    draw.text((190, 590), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text(
        (190, 670),
        f"Powered By: KING_BIOz  (@TAMIL_CHATBOX)",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    commandpro(["/play", "/yt", "/ytp", "play", "yt", "ytp", "@", "#"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    
    lel = await message.reply("**🔎 𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 processing✨😍. ...**")

    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "Aditya_Player"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "**💥 𝐀𝐃𝐌𝐈𝐍 𝐏𝐎𝐃𝐔 𝐅𝐈𝐑𝐒𝐓✨🙄 ...**")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 ..**")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"**🎸𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓 please manully add assistant here 👉[ @SunMusicAssiT ]✨🥰** ")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"**🎸𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 please manully add assistant here 👉[ @SunMusicAssiT ]✨🥰** ...*")
        return
    
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"**✅✨𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 Ƥɭɑy Ɱʋsɩƈ  Lɘss ⚡️\n🤟 Ƭɦɑɳ⚡️ {DURATION_LIMIT} 💞 Ɱɩɳʋʈɘ ...**"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/bba6f800202a4c6c08ff6.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="❰💫𝐒ᴏᴜʀᴄᴇ💕❱",
                            url=f"https://t.me/KING_BIOz")

                ]
            ]
        )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="❰💫𝐒ᴏᴜʀᴄᴇ💕❱",
                            url=f"https://t.me/KING_BIOz")

                ]
            ]
        )

        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/40669a772e9cc71b77edf.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="❰💫𝐒ᴏᴜʀᴄᴇ💕❱",
                            url=f"https://t.me/KING_BIOz")

                ]
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**✅✨𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 Ƥɭɑy 🔊 Ɱʋsɩƈ 💿 Lɘss ⚡️\n🤟 Ƭɦɑɳ⚡️ {DURATION_LIMIT} 💞 Ɱɩɳʋʈɘ ...**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "**😱𝙊𝙃𝙒 𝙊𝙊 𝙉𝘼𝙉𝘼. 𝘼𝘿𝙃𝙐 𝙎𝘼𝙍𝙄 𝙎𝙊𝙉𝙂 𝙉𝘼𝙈𝙀 𝙔𝘼𝘼𝙍𝙐 𝙐𝙉 𝙏𝙃𝘼𝙏𝙃𝘼 𝙑𝘼𝙉𝘿𝙃𝙐 𝙋𝙊𝘿𝙐𝙑𝘼𝙍𝙊𝙊✨😂...**"
            )
        await lel.edit("**😍✨𝙎𝙐𝙈𝙈𝘼 𝙂𝙀𝙏𝙃𝘼 Connecting to vc 𝙀𝙉𝙄 𝙈𝘼𝙅𝘼 𝘿𝙃𝘼𝙉 𝘿𝙊𝙄 ✨💃...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "**🔊 𝐋𝐎𝐋 𝐆𝐀𝐍𝐀 𝐇𝐈 𝐍𝐈 𝐌𝐈𝐋𝐀 𝐘𝐑 𝐒𝐀𝐇𝐈 𝐒𝐄 𝐋𝐈𝐊𝐇 𝐊𝐄 𝐃𝐄𝐊𝐇 1 𝐎𝐑 𝐁𝐀𝐑🌷...**"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="❰💙𝐂ʜᴀɴɴᴇʟ❤️❱",
                            url=f"https://t.me/KING_BIOz")

                ]
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**✅✨𝐒𝐔𝐍 𝐌𝐔𝐒𝐈𝐂 Ƥɭɑy 🔊 Ɱʋsɩƈ 💿 Lɘss ⚡️\n🤟 Ƭɦɑɳ⚡️ {DURATION_LIMIT} 💞 Ɱɩɳʋʈɘ ...**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) in ACTV_CALLS:
        position = await queues.put(chat_id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption="**🥰✨𝐖𝐀𝐈𝐓 𝐏𝐀𝐍𝐍𝐔 𝐌𝐀𝐂𝐇𝐈 Song Qued» `{}` 🌷 ...**".format(position),
            reply_markup=keyboard,
        )
    else:
        await clientbot.pytgcalls.join_group_call(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )

        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**💥🎧𝐋𝐚𝐥𝐚𝐥𝐚 𝐞𝐧𝐧𝐚 𝐩𝐚𝐤𝐫𝐚 𝐧𝐨𝐰 𝐦𝐢 Playing 💃**".format(),
           )

    os.remove("final.png")
    return await lel.delete()
    
    
@Client.on_message(commandpro(["/pause", "pause"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    await clientbot.pytgcalls.pause_stream(message.chat.id)
    await message.reply_photo(
                             photo="https://telegra.ph/file/48943ea9491b01179026b.jpg", 
                             caption="**𝙀𝙉𝙉𝘼 𝙏𝙃𝘼𝙇𝘼 𝙋𝘼𝙐𝙎𝙀 𝙋𝘼𝙉𝙏𝘼✨🙄...**"
    )


@Client.on_message(commandpro(["/resume", "resume"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    await clientbot.pytgcalls.resume_stream(message.chat.id)
    await message.reply_photo(
                             photo="https://telegra.ph/file/b6aac9125e9d40a791409.jpg", 
                             caption="**🤩✨𝙑𝙀𝙍𝘼 𝙈𝘼𝘼𝙍𝙄 𝙉𝙊𝙒 𝙎𝙊𝙉𝙂 𝑷𝑳𝑨𝒀𝑰𝑵𝑮✨💃...**"
    )



@Client.on_message(commandpro(["/skip", "/next", "skip", "next"]) & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) not in ACTV_CALLS:
        await message.reply_text("*𝙉𝙀𝙓𝙏 𝙆𝙐𝘿𝙐𝙏𝙃𝘼 𝙋𝙊𝘿𝙃𝘼𝘿𝙃𝙐 𝙎𝙊𝙉𝙂 𝙋𝙇𝘼𝙔 𝙋𝘼𝙉𝙄𝙏𝙐 𝙉𝙀𝙓𝙏 𝙆𝙐𝘿𝙐✨🙄 ...**")
    else:
        queues.task_done(chat_id)
        
        if queues.is_empty(chat_id):
            await clientbot.pytgcalls.leave_group_call(chat_id)
        else:
            await clientbot.pytgcalls.change_stream(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        clientbot.queues.get(chat_id)["file"],
                    ),
                ),
            )


    await message.reply_photo(
                             photo="https://telegra.ph/file/f44b37306e9d2e9c2d5cb.jpg", 
                             caption=f'*🎧✨𝐒𝐎𝐍𝐆 𝐒𝐊𝐈𝐏𝐄𝐃✅...**'
   ) 


@Client.on_message(commandpro(["/end", "end", "/stop", "stop", "x"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
        clientbot.queues.clear(message.chat.id)
    except QueueEmpty:
        pass

    await clientbot.pytgcalls.leave_group_call(message.chat.id)
    await message.reply_photo(
                             photo="https://telegra.ph/file/2f580447690c54eeeda6d.jpg", 
                             caption="** 🚫✨𝙈𝙐𝙎𝙄𝘾 𝙀𝙉𝘿 𝙝𝙪𝙝 𝙤𝙠𝙞 𝙉𝙀𝙓𝙏 𝙏𝙄𝙈𝙀 𝙋𝘼𝙆𝘼𝙇𝘼𝙈✨🥰 ...**"
    )


@Client.on_message(commandpro(["reload", "refresh"]))
@errors
@authorized_users_only
async def admincache(client, message: Message):
    set(
        message.chat.id,
        (
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ),
    )

    await message.reply_photo(
                              photo="https://telegra.ph/file/6e7a7d3bc1a848804bdfa.jpg",
                              caption="**✅✨ 𝙏𝙄𝙈𝙀 𝙏𝙊 Ʀɘɭøɑɗɘɗ 🥰 ...**"
    )
