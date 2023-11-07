from bs4 import BeautifulSoup
import requests
import os
import yaml
from datetime import datetime
from abc import ABC, abstractmethod

class AbstractShelter(ABC):

    def __init__(self, url: str, name: str,):
        self.name = name
        self.url = url
        self.soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        self.cachepath = os.path.join("data", name.replace(" ", "_").lower(), "cats.yaml")
        if not os.path.exists(self.cachepath):
            os.makedirs(os.path.dirname(self.cachepath), exist_ok=True)
            with open(self.cachepath, "w") as f:
                yaml.dump({}, f)
    
    def read_cache(self) -> dict:
        with open(self.cachepath, "r") as f:
            return yaml.safe_load(f)

    def update_cache(self, cats) -> dict:
        with open(self.cachepath, "w") as f:
            yaml.dump(cats, f)

    @abstractmethod
    def get_cats(self) -> dict:
        pass

    def update(self):
        def _filtercommon(a, b):
            if a is None or b is None:
                return a
            return {key: a[key] for key in set(a.keys()) - set(b.keys())}
        
        try:
            cached_cats = self.read_cache()
            new_cats = self.get_cats()
            self.update_cache(new_cats)
            return {"new_cats": _filtercommon(new_cats, cached_cats), "adopted_cats": _filtercommon(cached_cats, new_cats)}
        except Exception as e:
            with open(os.path.join("logs", "error.txt"), "a") as f:
                f.write(f"Error in {self.name} at {datetime.now()}: {e}\n")
            return {"new_cats": {}, "adopted_cats": {}}


