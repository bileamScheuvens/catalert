import os
import yaml
import asyncio
import requests
from io import BytesIO
from telegram import Bot
from datetime import datetime

from shelters import *

SOURCES = [
    KAShelter(),
    MAShelter(),
    BNShelter(),
    HNShelter(),
    KoelnShelter(),
    SBShelter(),
    LUShelter(),
]

with open("recipients.txt") as f:
    RECIPIENTS = f.read().splitlines()

bot = Bot(token=yaml.safe_load(open("secrets.yaml"))["bot_token"])


async def send_message(recipient, message):
    await bot.send_message(chat_id=recipient, text=message)


async def send_image(recipient, img):
    await bot.send_photo(chat_id=recipient, photo=BytesIO(img))


async def run():
    async def _send_update(cats, shelter_name, template):
        for cat_name, img_url in cats.items():
            plural_conditional = (
                "sind" if any(x in cat_name for x in ["&", "und", ","]) else "ist"
            )
            img_response = requests.get(img_url)
            for recipient in RECIPIENTS:
                await send_message(
                    recipient,
                    template.format(
                        cat_name=cat_name,
                        pl_cond=plural_conditional,
                        shelter_name=shelter_name,
                    ),
                )
                if img_response.status_code == 200:
                    await send_image(recipient, img_response.content)

    for shelter in SOURCES:
        changes = shelter.update()
        new_cats = changes["new_cats"]
        adopted_cats = changes["adopted_cats"]
        def _log(prefix, cats):
            with open(os.path.join("logs", "log.txt"), "a") as f:
                f.write(
                    f"{datetime.now()} - {shelter.name}: {prefix} {cats} \n"
                )
        if new_cats:
            _log("++", " & ".join(new_cats.keys()))
            await _send_update(
                new_cats,
                shelter.name,
                "{cat_name} {pl_cond} frisch frei zur Adoption von {shelter_name} 🐱!",
            )
        if adopted_cats:
            _log("--", " & ".join(adopted_cats.keys()))
            await _send_update(
                adopted_cats,
                shelter.name,
                "{cat_name} {pl_cond} aus {shelter_name} adoptiert! Alles Gute im neuen Zuhause 🚀!",
            )


if __name__ == "__main__":
    asyncio.run(run())
