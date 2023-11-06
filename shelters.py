from abstractshelter import AbstractShelter
import requests
from bs4 import BeautifulSoup


class KAShelter(AbstractShelter):
    def __init__(self):
        super().__init__(
            "https://www.tierheim-karlsruhe.de/katzen/", "Tierheim Karlsruhe"
        )

    def get_cats(self) -> dict:
        return {
            cat.h2.a.get_text(): cat.find("img")["src"]
            for cat in self.soup.find(class_="animals-table")
        }


class MAShelter(AbstractShelter):
    def __init__(self):
        super().__init__(
            "https://www.tierheim-mannheim.de/katzen/", "Tierheim Mannheim"
        )

    def get_cats(self) -> dict:
        names = [x.get_text() for x in self.soup.find_all(class_="wk-link-reset")]
        imgs = []
        for x in self.soup.find_all(class_="wk-position-cover wk-position-z-index"):
            new_page = BeautifulSoup(requests.get(x.get("href")).content, "html.parser")
            imgs.append(
                new_page.find(class_="uk-margin-medium-top").find("img").get("src")
            )

        return dict(zip(names, imgs))


class BNShelter(AbstractShelter):
    def __init__(self):
        super().__init__(
            "https://tierheimbonn.de/unsere-katzen/", "Tierheim Albert Schweitzer Bonn"
        )

    def clean_name(self, name):
        name = name.replace("\n", "")
        name = name.replace("\t", "")
        name = name.split("gerne")[0]
        name = name.split(",")[0]
        name = name.split("(")[0]
        name = name.split("-")[0]
        name = name.split(":")[1] if ":" in name else name
        name = name.split("–")[0]
        name = name.replace("Private Vermittlungshilfe", "")
        name = name.replace("als Paar", "")
        name = name.replace("nur", "")
        return name.strip()

    def get_cats(self) -> dict:
        return {
            self.clean_name(cat.find("h5").get_text()): cat.find("img")["src"]
            for cat in self.soup.find_all(class_="elementor-portfolio-item")
        }


class StuttgartShelter(AbstractShelter):
    def __init__(self):
        super().__init__(
            "https://stuttgarter-tierschutz.de/", "Tierschutzverein Stuttgart"
        )

    def get_cats(self) -> dict:
        # BROKEN
        # SCRAPE PROTECTED :(
        self.soup.find("div", id="div_tiere_nav_wrapper")
        return {
            cat.h2.a.get_text(): cat.find("img")["src"]
            for cat in self.soup.find(class_="table_tiere_left_td")
        }
