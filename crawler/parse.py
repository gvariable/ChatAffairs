import aiohttp
from lxml import etree
import ipdb

with open("meta.html", "r") as f:
    html = f.read()

# print(html)

root = etree.HTML(html)
lis = root.xpath('//*[@class="contentList"]/ul/li')


strip_non_empty = lambda x: list(
    map(lambda x: x.strip(), filter(lambda x: x.strip(), x))
)

for li in lis[0:3]:
    tag = strip_non_empty(li.xpath("./div[1]//text()"))[0]
    print(tag)

    tables = li.xpath(".//table")
    for table in tables:
        # maybe empty
        table_title = strip_non_empty(table.xpath('.//tr[@class="title_tr"]//text()'))
        trs = table.xpath('.//tr[not(contains(@class, "title"))]')
        if table_title:
            print(table_title[0])

        for tr in trs:
            td = strip_non_empty(tr.xpath(".//text()"))
            td = [td[0], "".join(td[1:])]
            print(td)
