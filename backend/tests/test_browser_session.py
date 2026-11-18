import asyncio

from browser.session import browser_session


async def main():

    async with browser_session(headless=True) as page:

        await page.set_content("""
            <html>
                <head>
                    <title>WebForm Agent</title>
                </head>
                <body>
                    <h1>Browser Infrastructure Test</h1>
                </body>
            </html>
        """)

        title = await page.title()

        assert title == "WebForm Agent"

        print("Browser session working:", title)


if __name__ == "__main__":
    asyncio.run(main())