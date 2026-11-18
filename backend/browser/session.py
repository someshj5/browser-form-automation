
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright


@asynccontextmanager
async def browser_session(headless: bool = False):

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(
            headless=headless,
            args=["--disable-notifications"]
        )

        context = await browser.new_context()

        page = await context.new_page()

        try:
            yield page

        finally:
            await context.close()
            await browser.close()
