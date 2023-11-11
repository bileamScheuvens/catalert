import yaml
import asyncio
import requests
from io import BytesIO
from telegram import Bot
from telegram.error import BadRequest
from utils import log, log_error
from ssl import SSLWantReadError
from asyncio.exceptions import CancelledError

from shelters import *

SOURCES = [
    KAShelter(),
    MAShelter(),
    BNShelter(),
    HNShelter(),
    KoelnShelter(),
    SBShelter(),
    LUShelter(),
    HHShelter(),
    MZShelter(),
    MUShelter()
]

with open("recipients.txt") as f:
    RECIPIENTS = f.read().splitlines()

bot = Bot(token=yaml.safe_load(open("secrets.yaml"))["bot_token"])

async def send_message(recipient, message):
    await bot.send_message(chat_id=recipient, text=message)


async def send_image(recipient, img, caption):
    try:
        await bot.send_photo(chat_id=recipient, photo=BytesIO(img), caption=caption)
    except SSLWantReadError as e:
        log_error(f"{recipient}: {e}", "SEND_IMAGE")
    except CancelledError as e:
        log_error(f"{recipient}: {e}", "SEND_IMAGE")


async def run(DRY_RUN=False):
    async def _send_update(cats, shelter_name, template):
        for cat_name, img_url in cats.items():
            plural_conditional = (
                "sind" if any(x in cat_name for x in ["&", "und", ","]) else "ist"
            )
            img_response = requests.get(img_url)
            for recipient in RECIPIENTS:
                message = template.format(
                    cat_name=cat_name,
                    pl_cond=plural_conditional,
                    shelter_name=shelter_name,
                )
                try:
                    if DRY_RUN:
                        pass
                    elif img_response.status_code == 200:
                        await send_image(recipient, img_response.content, caption=message)
                    else:
                        await send_message(recipient, message)
                except BadRequest as e:
                    log_error(f"ID INVALID {recipient}, {e}", "GLOBAL")


    for shelter in SOURCES:
        changes = shelter.update()
        new_cats = changes["new_cats"]
        adopted_cats = changes["adopted_cats"]
        
        if new_cats:
            log("++", " & ".join(new_cats.keys()), shelter.name)
            await _send_update(
                new_cats,
                shelter.name,
                "{cat_name} {pl_cond} frisch frei zur Adoption von {shelter_name}! 🐱",
            )
        if adopted_cats:
            log("--", " & ".join(adopted_cats.keys()), shelter.name)
            await _send_update(
                adopted_cats,
                shelter.name,
                "{cat_name} {pl_cond} aus {shelter_name} adoptiert! Alles Gute im neuen Zuhause! 🚀",
            )


if __name__ == "__main__":
    asyncio.run(run(DRY_RUN=False))
