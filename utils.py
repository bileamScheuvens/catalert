import os
from datetime import datetime

def log(prefix, cats, shelter_name=None):
    with open(os.path.join("logs", "log.txt"), "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} - {shelter_name}: {prefix} {cats} \n"
        )

def log_error(e, src=""):
    with open(os.path.join("logs", "error.txt"), "a") as f:
        f.write(f"{datetime.now()}: Error in {src} - {e}\n")