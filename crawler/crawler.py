import json
from parse import AffairParser
import asyncio
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm
from pathlib import Path


async def fetch(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        text = await page.content()
        await browser.close()
        return text


async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await tqdm.gather(*tasks, leave=False, desc="Fetching websites")


async def schedule_task(metas, urls):
    # split task into several pieces

    dir = Path("htmls")
    if not dir.exists():
        dir.mkdir()
    workers = 30

    for i in tqdm(range(len(urls) // workers), desc="Scheduling tasks"):
        texts = await fetch_all(urls[i * workers : (i + 1) * workers])
        for meta, text in zip(metas[i * workers : (i + 1) * workers], texts):
            path = dir / f"{meta['taskCode']}.html"
            if not path.exists():
                path.write_text(text)

    # the last remaining piece
    texts = await fetch_all(urls[len(urls) // workers * workers :])
    for meta, text in zip(metas[len(urls) // workers * workers :], texts):
        path = dir / f"{meta['taskCode']}.html"
        if not path.exists():
            path.write_text(text)


async def main():
    with open("gov.json", "r") as f:
        metas = json.load(f)
    base_url = (
        "http://zwfw.hubei.gov.cn/webview/bszn/bsznpage.html?transactCode={taskCode}"
    )

    urls = [base_url.format(taskCode=meta["taskCode"]) for meta in metas]
    await schedule_task(metas, urls)


if __name__ == "__main__":
    asyncio.run(main())
