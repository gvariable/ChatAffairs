import aiohttp
import json
from parse import AffairParser
import asyncio

COUNT = 0


async def fetch(session: aiohttp.ClientSession, url):
    global COUNT
    async with session.get(url) as resp:
        text = await resp.text()
        COUNT += 1
        print(f"count: {COUNT}, status: {resp.status}, fetch {url} complete")
        return text


async def fetch_all(urls):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Connection": "keep-alive",
        "Cookie": "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221891651735d108b-0cebc77e7a5cbf8-49193201-1296000-1891651735e14c2%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221891651735d108b-0cebc77e7a5cbf8-49193201-1296000-1891651735e14c2%22%7D; Hm_lpvt_2e78e4e6592603c96de5e3ada929877c=1688379845; Hm_lvt_2e78e4e6592603c96de5e3ada929877c=1688289029; SESSIONID=MmIxNmUyZGQtNDcwMC00NTJiLWFkNTAtOWY3N2JjNGU3Mjlk",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(fetch(session, url)))
        return await asyncio.gather(*tasks)


async def main():
    with open("gov.json", "r") as f:
        metas = json.load(f)
    base_url = (
        "http://zwfw.hubei.gov.cn/webview/bszn/bsznpage.html?transactCode={taskCode}"
    )

    urls = []
    for i in range(3):
        urls.append(base_url.format(taskCode=metas[i]["taskCode"]))
    for idx, text in enumerate(await fetch_all(urls)):
        with open(f"text_{idx}.json", "w") as f:
            f.write(text)


if __name__ == "__main__":
    asyncio.run(main())
