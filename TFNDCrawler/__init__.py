import os
import re
import httpx
import toml
from bs4 import BeautifulSoup as BS


class TFNDCrawler():
    def __init__(self):
        filedir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(filedir, "config.toml")) as fd:
            self.config = toml.load(fd)
        self.URL = self.config.get("URL")

    def search(self):
        queryURL = self.URL
        res = httpx.get(queryURL)
        soup = BS(res.text, "html.parser")
        content = soup.find("div", class_="content")
        sz = int(content.find("span").text)
        m = re.match(r".*共有(\d+)頁.*", content.find("div", class_="page").text,
                     re.DOTALL)
        maxpage = int(m.group(1))
        results = []
        keys = ["整合編號", "樣品名稱", "俗名", "樣品英文名稱", "內容物描述"]
        for i in range(1, maxpage + 1):
            res = httpx.get(f"{queryURL}&p={i}")
            soup = BS(res.text, "html.parser")
            content = soup.find("div", class_="content")
            for tr in content.find_all("tr")[1:]:
                result = {}
                for key, td in zip(keys, tr.find_all("td")[1:]):
                    result[key] = td.text.strip()
                results.append(result)
        assert len(results) == sz
        return results
