import datetime
import os
import random

from gevent.monkey import patch_all
patch_all(thread=False, select=False)

from vkwave.api.methods._error import APIError
from vkwave.bots import (DocUploader, PhotoUploader, SimpleBotEvent,
                         SimpleLongPollBot)

from db.config import GROUP_ID, TOKEN
from image_creator import create_picture

bot = SimpleLongPollBot(tokens=TOKEN, group_id=GROUP_ID)

photo_uploader = PhotoUploader(api_context=bot.api_context)
file_uploader = DocUploader(api_context=bot.api_context)


@bot.message_handler(bot.command_filter(["life", "live", "check"]))
async def life(_):
    return "alive"


@bot.message_handler()
async def main(event: SimpleBotEvent):
    t = event.object.object.message.text

    text = t.split()

    if t == "Начать" and event.peer_id < 2000000000:
        return "Привет. Отправь мне код колоды для того, чтобы я " \
               "сгенерировать картинку по нему для удобного отображения." \
               "Также я поддерживаю возможность автоматически " \
               "обнаруживать сообщения содержащие " \
               "коды внутри активных бесед." \
               "Для этого добавьте меня и выдайте админские права через " \
               "кнопку на главной странице сообщества."

    for word in text:
        if word[:2] == "AA":
            time_start = datetime.datetime.now()
            image = await create_picture(word)
            if not image:
                return
            print("time creating: ", datetime.datetime.now() - time_start)
            name = random.randint(1000000, 10000000)

            time_start = datetime.datetime.now()
            if event.peer_id > 2000000000:
                x, y = image.size
                image = image.resize((int(x / 2), int(y / 2)))
            image.save(f"{name}.png", format="PNG")
            print("time saving: ", datetime.datetime.now() - time_start)
            resp_doc = ""

            time_start = datetime.datetime.now()

            try:
                resp = await photo_uploader.get_attachment_from_path(
                    peer_id=event.peer_id, file_path=f"{name}.png",
                    file_extension="png")

                if event.peer_id < 2000000000:
                    resp_doc = await file_uploader.get_attachment_from_path(
                        peer_id=event.peer_id, file_path=f"{name}.png",
                        file_extension="png")
            except APIError:
                try:
                    resp = await photo_uploader.get_attachment_from_path(
                        peer_id=event.user_id, file_path=f"{name}.png",
                        file_extension="png")
                except APIError:
                    return "Отправь сообщение мне в лс, " \
                           "чтобы я мог отправить фото с колодой"

            await event.answer(attachment=f"{resp},{resp_doc}")
            print("time sending:", datetime.datetime.now() - time_start)

            os.remove(f"{name}.png")
            print("image_deleted")


bot.run_forever()
