import os
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from abc import ABC, abstractmethod
from utils import log_error


class AbstractShelter(ABC):
    def __init__(
        self,
        url: str,
        name: str,
    ):
        self.name = name
        self.url = url
        self.soup = BeautifulSoup(requests.get(url).content, "html.parser")
        self.cachepath = os.path.join(
            "data", name.replace(" ", "_").lower(), "cats.yaml"
        )
        if not os.path.exists(self.cachepath):
            os.makedirs(os.path.dirname(self.cachepath), exist_ok=True)
            with open(self.cachepath, "w") as f:
                yaml.dump({}, f)

    def read_cache(self) -> dict:
        with open(self.cachepath, "r") as f:
            return yaml.safe_load(f)

    def update_cache(self, cats) -> dict:
        with open(self.cachepath, "w") as f:
            yaml.dump(cats, f, allow_unicode=True)

    @abstractmethod
    def get_cats(self) -> dict:
        pass

    def clean_name(self, name) -> str:
        name = name.replace("\n", "")
        name = name.replace("\t", "")
        name = name.replace(" und ", " & ")
        return name.strip().title()

    def update(self):
        def _filtercommon(a, b):
            if a is None or b is None:
                return a
            return {key: a[key] for key in set(a.keys()) - set(b.keys())}

        try:
            cached_cats = self.read_cache()
            new_cats = {self.clean_name(k):v for k,v in self.get_cats().items()}
            self.update_cache(new_cats)
            return {
                "new_cats": _filtercommon(new_cats, cached_cats),
                "adopted_cats": _filtercommon(cached_cats, new_cats),
            }
        except Exception as e:
            log_error(e, self.name)
            return {"new_cats": {}, "adopted_cats": {}}
