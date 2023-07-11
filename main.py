import os
import random

import grequests
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
            print(word)
            image = await create_picture(word)
            if not image:
                return
            print("image_created")
            name = random.randint(1000000, 10000000)

            image.save(f"{name}.png", format="PNG")
            print("image_saved")

            resp = await photo_uploader.get_attachment_from_path(
                peer_id=event.peer_id, file_path=f"{name}.png",
                file_extension="png")

            resp_doc = ""
            if event.peer_id < 2000000000:
                resp_doc = await file_uploader.get_attachment_from_path(
                    peer_id=event.peer_id, file_path=f"{name}.png",
                    file_extension="png")

            await event.answer(attachment=f"{resp},{resp_doc}")
            print("image_sent")

            os.remove(f"{name}.png")
            print("image_deleted")


bot.run_forever()
