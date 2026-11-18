
import asyncio
from playwright.async_api import async_playwright


async def main():

    async with async_playwright() as p:

        # 1. Launch Chromium
        print("Launching Chromium...")

        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300,
            args=["--disable-notifications"]
        )

        print("Browser launched!")

        # 2. Create a new browser tab
        page = await browser.new_page()

        # 3. Load our test HTML
        await page.set_content("""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>WebForm Agent - Test Page</title>
                </head>

                <body>
                    <h1>Customer Registration</h1>

                    <form>

                        <label for="customer-name">
                            Full Name
                        </label>

                        <input
                            id="customer-name"
                            name="full_name"
                            type="text"
                            placeholder="Enter your name"
                            required
                        />

                        <label for="customer-email">
                            Email Address
                        </label>

                        <input
                            id="customer-email"
                            name="email"
                            type="email"
                            placeholder="Enter your email"
                            required
                        />

                        <label for="customer-message">
                            Message
                        </label>

                        <textarea
                            id="customer-message"
                            name="message"
                            placeholder="Enter your message"
                        ></textarea>

                        <button type="submit">
                            Submit
                        </button>

                    </form>
                </body>
            </html>
        """)

        print("Page title:", await page.title())

        # 4. Find all input elements
        inputs = page.locator("input")

        count = await inputs.count()

        print("\nTotal input fields:", count)

        # 5. Locate email input
        email_input = page.locator("input[type='email']")

        print("\nEmail field count:", await email_input.count())

        print(
            "Email name:",
            await email_input.get_attribute("name")
        )

        print(
            "Email ID:",
            await email_input.get_attribute("id")
        )

        print(
            "Email placeholder:",
            await email_input.get_attribute("placeholder")
        )

        print(
            "Current email value:",
            await email_input.input_value()
        )

        # 6. Find all form controls
        fields = page.locator("input, textarea, select")

        print(
            "\nTotal form controls:",
            await fields.count()
        )

        # 7. Extract metadata from all input elements
        input_metadata = await inputs.evaluate_all("""
            elements => elements.map(el => ({

                tag: el.tagName.toLowerCase(),

                type: el.type,

                name: el.name,

                id: el.id,

                label: Array.from(el.labels || [])
                    .map(label => label.innerText.trim())
                    .join(" "),

                placeholder: el.placeholder,

                required: el.required,

                disabled: el.disabled

            }))
        """)

        # 8. Display extracted metadata
        print("\\nExtracted Input Metadata:")

        for field in input_metadata:
            print(field)

        # 9. Keep browser open for inspection
        print("\\nBrowser is open. Press ENTER to close.")

        input()

        # 10. Close browser
        await browser.close()

        print("Browser closed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
