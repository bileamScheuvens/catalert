import requests
from bs4 import BeautifulSoup

from abstractshelter import AbstractShelter


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

class HNShelter(AbstractShelter):
    def __init__(self):
        super().__init__("https://www.heilbronner-tierschutz.de/tiervermittlung/katzen/", "Tierschutzverein Heilbronn")

    def get_cats(self) -> dict:
        return {cat.a.get("title"): cat.a.img.get("src") for cat in self.soup.find_all(class_="qode-post-image")}
    
class KoelnShelter(AbstractShelter):
    def __init__(self):
        super().__init__("https://tierheim-koeln-dellbrueck.de/vermittlung/katzen", "Tierheim Koeln Dellbrueck")
    
    def clean_name(self, name):
        name = name.split("(")[0]
        return name.strip()

    def get_cats(self) -> dict:
        return {self.clean_name(cat.img.get("alt")): cat.img.get("src") for cat in self.soup.find_all("figure")}

class SBShelter(AbstractShelter):
    def __init__(self):
        super().__init__("https://www.tierheim-saarbruecken.de/zuhause-gesucht/katzen", "Tierheim Saarbruecken")
    
    def clean_name(self, name):
        name = name.replace("\n", "")
        name = name.replace("\t", "")
        name = name.replace("!!! Notfall !!!", "")
        return name.strip()

    def get_cats(self) -> dict:
        names = [self.clean_name(cat.get_text()) for cat in self.soup.find_all("h2")]
        imgs = ["https://www.tierheim-saarbruecken.de/"+cat.img.get("src") for cat in self.soup.find_all(class_="item active")]
        return dict(zip(names, imgs))
    
class LUShelter(AbstractShelter):
    def __init__(self):
        super().__init__("https://tierheim-ludwigshafen.com/katzen/", "Tierheim Ludwigshafen")

    def get_cats(self) -> dict:
        return {cat.img.get("alt"): cat.img.get("src") for cat in self.soup.find_all(class_="et_portfolio_image")}