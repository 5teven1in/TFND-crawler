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

    def makequery(self, kw, tagtype, searchfield):
        f = ""
        for field in searchfield:
            f += self.config.get("SearchField").get(field)
            f += ","
        t = self.config.get("TagType").get(tagtype)
        url = f"{self.URL}{self.config.get('queryURI')}&t={t}&f={f}&k={kw}"
        return url

    def search(self, kw="", tagtype="全部", searchfield=[]):
        queryURL = self.makequery(kw, tagtype, searchfield)
        res = httpx.get(queryURL)
        soup = BS(res.text, "html.parser")
        content = soup.find("div", class_="content")
        sz = int(content.find("span").text)
        m = re.match(r".*共有(\d+)頁.*", content.find("div", class_="page").text,
                     re.DOTALL)
        maxpage = int(m.group(1)) if m else 1
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
                    if key == "整合編號":
                        ty = str(ord(result["整合編號"][0]) - ord("A") + 1)
                        ty = list(self.config.get(
                            "TagType").values()).index(ty)
                        result["食品分類"] = list(
                            self.config.get("TagType").keys())[ty]
                    if key == "樣品名稱":
                        result["ID"] = td.find("a").get("href").split("=")[-1]
                results.append(result)
        assert len(results) == sz
        return results

    def getdetail(self, ID):
        res = httpx.get(
            f"{self.URL}{self.config.get('detailURI')}&f=0&id={ID}")
        soup = BS(res.text, "html.parser")
        results = []
        for tr in soup.find("table").find_all("tr")[1:]:
            result = {}
            for td in tr.find_all("td")[:-2]:
                result[td.get("data-th")] = td.text.strip()
            results.append(result)
        return results
