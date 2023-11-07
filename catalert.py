import os
import yaml
import asyncio
import requests
from io import BytesIO
from telegram import Bot
from datetime import datetime

from shelters import KAShelter, MAShelter, BNShelter

SOURCES = [
    KAShelter(),
    MAShelter(),
    BNShelter(),
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
                "sind" if "&" in cat_name or "und" in cat_name else "ist"
            )
            img = requests.get(img_url).content
            for recipient in RECIPIENTS:
                await send_message(
                    recipient,
                    template.format(
                        cat_name=cat_name,
                        pl_cond=plural_conditional,
                        shelter_name=shelter_name,
                    ),
                )
                await send_image(recipient, img)

    for shelter in SOURCES:
        changes = shelter.update()
        new_cats = changes["new_cats"]
        adopted_cats = changes["adopted_cats"]
        with open(os.path.join("logs", "log.txt"), "a") as f:
            f.write(
                f"{datetime.now()} - {shelter.name}: ++{' '.join(new_cats.keys())} --{' '.join(adopted_cats.keys())} \n"
            ) if any(changes.values()) else None
        if new_cats:
            await _send_update(
                new_cats,
                shelter.name,
                "{cat_name} {pl_cond} frisch frei zur Adoption von {shelter_name} 🐱!",
            )
        if adopted_cats:
            await _send_update(
                adopted_cats,
                shelter.name,
                "{cat_name} {pl_cond} aus {shelter_name} adoptiert! Alles Gute im neuen Zuhause 🚀!",
            )


if __name__ == "__main__":
    asyncio.run(run())
