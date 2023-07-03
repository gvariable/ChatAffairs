import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re
import json
import time


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        page.set_default_timeout(3000)

        await page.goto(
            "http://zwfw.hubei.gov.cn/webview/fw/grfw.html",
            wait_until="domcontentloaded",
        )
        print(await page.title())

        metas = []
        while True:
            # TODO(gpl): wait for page to load
            await page.wait_for_load_state("load")
            time.sleep(0.3)

            # traverse every page
            subjects = page.locator('//*[@class="mulu_item"]')
            await subjects.first.wait_for()

            # traverse every subject
            for subject in await subjects.all():
                # collect meta info
                title = await subject.locator('xpath=.//div[@class="title_text"]').inner_text()
                addition = await subject.locator('xpath=.//div[@class="title_add"]').inner_text()
                subject_meta = {"title": title, "addition": addition}
                print(f"{title}, {addition}")
                
                # click to open subitem
                await subject.click()

                items = subject.locator('xpath=.//*[@class="ywblxItem"]')
                try:
                    await items.first.wait_for(state="attached")
                except TimeoutError:
                    # no items
                    continue

                for item in await items.all():
                    pat = r"'(\d\w+)'"
                    onclick = await item.get_attribute("onclick")
                    subtitle = await item.inner_text()
                    match = re.search(pat, onclick)
                    print(f"{subtitle}, {match.group(1)}")

                    subject_meta.update(
                        {"subtitle": subtitle, "taskCode": match.group(0)}
                    )
                    metas.append(subject_meta.copy())
            print()

            # pagination
            downpage = page.locator('//*[@class="downPage"]')
            await downpage.wait_for()

            if not await downpage.get_attribute("onclick"):
                break
            await downpage.click()

        await browser.close()
        with open("gov.json", "w") as f:
            json.dump(metas, f, indent=4, ensure_ascii=False)
        print("finished!")


asyncio.run(main())
