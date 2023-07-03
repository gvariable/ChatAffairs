import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.set_default_timeout(3000)

        await page.goto(
            "http://zwfw.hubei.gov.cn/webview/fw/grfw.html",
            wait_until="domcontentloaded",
        )
        print(await page.title())

        while True:
            # traverse every page
            await page.wait_for_selector('//*[@class="mulu_item"]')
            subjects = page.locator('//*[@class="mulu_item"]')

            # traverse every subject
            for subject in await subjects.all():
                title = await subject.locator(
                    'xpath=.//div[@class="title_text"]'
                ).inner_text()
                addition = await subject.locator(
                    'xpath=.//div[@class="title_add"]'
                ).inner_text()

                print(f"{title}, {addition}")

                await subject.click()

                items = subject.locator('xpath=.//*[@class="ywblxItem"]')
                try:
                    await items.wait_for()
                except TimeoutError:
                    continue

                for item in await items.all():
                    pat = r"'(\d\w+)'"
                    onclick = await item.get_attribute("onclick")
                    subtitle = await item.inner_text()
                    match = re.search(pat, onclick)
                    if match:
                        print(f"{subtitle}, {match.group(0)}")
                    else:
                        print(subtitle)
            print()

            # pagination
            downpage = page.locator('//*[@class="downPage"]')

            if not await downpage.get_attribute("onclick"):
                break
            await downpage.click()

        await browser.close()
        print("finished!")


asyncio.run(main())
