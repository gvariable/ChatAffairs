from lxml import etree
from itertools import zip_longest
import json
from pathlib import Path
import json_stream
from json_stream.writer import streamable_list


class AffairParser(object):
    def __init__(self, text) -> None:
        self.text = text
        self.metas = []

    def strip_non_empty(self, x):
        return list(map(lambda x: x.strip(), filter(lambda x: x.strip(), x)))

    def _parse_ol(self, lis):
        metas = []
        for li in lis[3:9]:
            meta = {}

            title = self.strip_non_empty(li.xpath("./div[1]//text()"))
            if title:
                meta["标题"] = title[0]
            else:
                continue

            if title[0] == "中介服务":
                texts = filter(
                    lambda x: x != "·", self.strip_non_empty(li.xpath(".//tr//text()"))
                )
                tds = list(zip_longest(*[iter(texts)] * 2, fillvalue=None))
                for td in tds:
                    meta[td[0]] = td[1]
            else:
                tables = li.xpath(".//table")
                for table in tables:
                    data = {}

                    trs = table.xpath(".//tr")
                    subtitle = " ".join(self.strip_non_empty(trs[0].xpath(".//text()")))
                    print(subtitle)

                    for tr in trs[1:]:
                        td = self.strip_non_empty(tr.xpath(".//text()"))
                        td = [td[0], "".join(td[1:])]
                        data[td[0]] = td[1]
                        print(td)

                    meta[subtitle] = data
            metas.append(meta)
            return metas

    def _parse_table(self, lis):
        metas = []
        for li in lis:
            meta = {}

            title = self.strip_non_empty(li.xpath("./div[1]//text()"))[0]
            meta["标题"] = title

            tables = li.xpath(".//table")
            for table in tables:
                data = {}
                trs = table.xpath('.//tr[not(contains(@class, "title"))]')
                for tr in trs:
                    td = self.strip_non_empty(tr.xpath(".//text()"))
                    td = [td[0], "".join(td[1:])]
                    data[td[0]] = td[1]

                # maybe empty
                subtitle = self.strip_non_empty(
                    table.xpath('.//tr[@class="title_tr"]//text()')
                )
                if subtitle:
                    meta[subtitle[0]] = data
                else:
                    meta[title] = data

            metas.append(meta)
        return metas

    def parse(self):
        root = etree.HTML(self.text)
        lis = root.xpath('//*[@class="contentList"]/ul/li')
        self.metas.extend(self._parse_table(lis[:3]))
        self.metas.extend(self._parse_ol(lis[3:9]))
        return self.metas


def save_json(html_dir: Path, data_dir: Path, meta_fn: Path):
    with open(meta_fn, "r") as f:
        for meta in json_stream.load(f):
            meta = json_stream.to_standard_types(meta)
            html_fn = html_dir / f"{meta['taskCode']}.html"
            data_fn = data_dir / f"{meta['taskCode']}.json"

            parser = AffairParser(html_fn.read_text())
            text = parser.parse()
            meta.update({"详情": text})

            data_fn.write_text(json.dumps(meta, indent=4, ensure_ascii=False))
            yield meta


if __name__ == "__main__":
    html_dir = Path("htmls")
    data_dir = Path("data")
    meta_fn = Path("gov.json")
    whole = Path("data.json")

    if not data_dir.exists():
        data_dir.mkdir()

    data = streamable_list(save_json(html_dir, data_dir, meta_fn))
    with open(whole, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
