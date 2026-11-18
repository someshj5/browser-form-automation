import asyncio

from playwright.async_api import async_playwright # type: ignore

from browser.dom_inspector import inspect_form


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_content("""
            <form>
                <label for="name">Full Name</label>
                <input
                    id="name"
                    name="full_name"
                    type="text"
                    required
                />

                <label for="email">Email Address</label>
                <input
                    id="email"
                    name="email"
                    type="email"
                    required
                />

                <label for="country">Country</label>
                <select id="country" name="country" required>
                    <option value="">Select country</option>
                    <option value="india">India</option>
                    <option value="usa">USA</option>
                </select>

                <label for="newsletter">Subscribe to newsletter</label>
                <input
                    id="newsletter"
                    name="newsletter"
                    type="checkbox"
                >

                <p>Preferred contact method</p>
                <label>
                    <input type="radio" name="contact" value="email">
                    Email
                </label>
                <label>
                    <input type="radio" name="contact" value="phone">
                    Phone
                </label>


                <textarea name="message"></textarea>

                <button type="submit">Submit</button>
            </form>
        """)

        fields = await inspect_form(page)


        for field in fields:
            print(field.model_dump())
            print("Field type:", type(field).__name__)

        # for field in metadata:
        #     print(field)

        # for field in fields:
        #     print(field)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())