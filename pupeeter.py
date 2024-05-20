import asyncio
from pyppeteer import launch

async def fetch_page_content(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    content = await page.content()
    await browser.close()
    return content

async def main():
    url = "https://www.frenchery.com"
    content = await fetch_page_content(url)
    print(content)

if __name__ == '__main__':
    asyncio.run(main())
