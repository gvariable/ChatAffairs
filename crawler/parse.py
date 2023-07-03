import aiohttp
from lxml import etree
from itertools import zip_longest
import json

with open("meta.html", "r") as f:
    html = f.read()

# print(html)

root = etree.HTML(html)
lis = root.xpath('//*[@class="contentList"]/ul/li')


metas = []

strip_non_empty = lambda x: list(
    map(lambda x: x.strip(), filter(lambda x: x.strip(), x))
)

for li in lis[0:3]:
    meta = {}

    title = strip_non_empty(li.xpath("./div[1]//text()"))[0]
    meta["标题"] = title

    tables = li.xpath(".//table")
    for table in tables:
        data = {}
        trs = table.xpath('.//tr[not(contains(@class, "title"))]')
        for tr in trs:
            td = strip_non_empty(tr.xpath(".//text()"))
            td = [td[0], "".join(td[1:])]
            data[td[0]] = td[1]
            # print(td)

        # maybe empty
        subtitle = strip_non_empty(table.xpath('.//tr[@class="title_tr"]//text()'))
        if subtitle:
            # print(subtitle[0])
            meta[subtitle[0]] = data
        else:
            meta[title] = data

    metas.append(meta)

for li in lis[3:9]:
    meta = {}

    title = strip_non_empty(li.xpath("./div[1]//text()"))
    if title:
        meta["标题"] = title[0]
        print(title[0])
    else:
        continue

    if title[0] == "中介服务":
        texts = filter(lambda x: x != "·", strip_non_empty(li.xpath(".//tr//text()")))
        tds = list(zip_longest(*[iter(texts)] * 2, fillvalue=None))
        for td in tds:
            meta[td[0]] = td[1]
    else:
        tables = li.xpath(".//table")
        for table in tables:
            data = {}

            trs = table.xpath(".//tr")
            subtitle = " ".join(strip_non_empty(trs[0].xpath(".//text()")))
            print(subtitle)

            for tr in trs[1:]:
                td = strip_non_empty(tr.xpath(".//text()"))
                td = [td[0], "".join(td[1:])]
                data[td[0]] = td[1]
                print(td)

            meta[subtitle] = data
    metas.append(meta)

print(json.dumps(metas, indent=4, ensure_ascii=False))
