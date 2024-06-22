import datetime
import os
import random

from patch import *

from vkbottle import PhotoMessageUploader, DocMessagesUploader, VKAPIError
from vkbottle.bot import Bot, Message

from db.config import TOKEN
from db.constants import BANNED
from image_creator import create_picture

bot = Bot(TOKEN)

photo_uploader = PhotoMessageUploader(bot.api)
file_uploader = DocMessagesUploader(bot.api)


def unpack_forward(message: Message):
    result = ""
    if message.fwd_messages:
        for i in message.fwd_messages:
            result += " " + unpack_forward(i)
    return message.text + " " + result


def unpack_repost(message: Message):
    res = " "
    for i in message.attachments:
        if i.wall:
            res += i.wall.text
    return res


@bot.on.message(text="Начать")
async def start_handler(message: Message):
    if message.peer_id < 2000000000:
        return "Привет. Отправь мне код колоды для того, чтобы я " \
               "сгенерировать картинку по нему для удобного отображения." \
               "Также я поддерживаю возможность автоматически " \
               "обнаруживать сообщения содержащие " \
               "коды внутри активных бесед." \
               "Для этого добавьте меня и выдайте админские права через " \
               "кнопку на главной странице сообщества."


@bot.on.message()
async def main_handler(message: Message):
    t = unpack_forward(message) + unpack_repost(message)
    text = t.split()
    for word in text:
        if word[:2] == "AA":
            if message.peer_id in BANNED:
                return "Группа забанена в Deck Viewer."

            time_start = datetime.datetime.now()
            try:
                image = await create_picture(word)
                if not image:
                    return
            except Exception as e:
                print(e)
                return ("Возникла ошибка в генерации."
                        "\nЕсли такое происходит постоянно, обратитесь к автору вместе с кодом.")

            print("time creating: ", datetime.datetime.now() - time_start)
            name = random.randint(1000000, 10000000)

            time_start = datetime.datetime.now()
            if message.peer_id > 2000000000:
                x, y = image.size
                image = image.resize((int(x / 2), int(y / 2)))
            image.save(f"{name}.png", format="PNG")
            print("time saving: ", datetime.datetime.now() - time_start)

            time_start = datetime.datetime.now()

            try:
                resp = await photo_uploader.upload(
                    file_source=f"{name}.png",
                    peer_id=message.peer_id)
            except VKAPIError[10]:
                try:
                    resp = await photo_uploader.upload(
                        file_source=f"{name}.png",
                        peer_id=message.from_id)
                except VKAPIError[10]:
                    return ("Возникла ошибка при отправке кода.\nВозможно у вас нет переписки"
                            "c ботом или проблема на стороне VK.")
            except Exception as e:
                print(e)
                try:
                    resp = await photo_uploader.upload(
                        file_source=f"{name}.png",
                        peer_id=message.peer_id)
                except Exception:
                    return 'Возникла проблема при отправке кода. Возможно поможет переотправка.'

            await message.answer(attachment=f"{resp}")
            print("time sending:", datetime.datetime.now() - time_start)

            if message.peer_id < 2000000000:
                resp_doc = await file_uploader.upload(
                    title=f"{word}.png",
                    file_source=f"{name}.png",
                    peer_id=message.peer_id)
                await message.answer(attachment=f"{resp_doc}")

            os.remove(f"{name}.png")
            print("image_deleted")


bot.run_forever()
