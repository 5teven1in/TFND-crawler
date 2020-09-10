import json
from TFNDCrawler import *


def main():
    crawler = TFNDCrawler()
    res = crawler.search(kw="蛋", tagtype="加工調理食品類",
                         searchfield=["樣品英文名稱", "樣品名稱"])

    print(json.dumps(res))
    # res = crawler.getdetail(29)
    # print(json.dumps(res))


if __name__ == "__main__":
    main()
