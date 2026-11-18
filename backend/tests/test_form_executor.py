
import asyncio

from browser.session import browser_session
from browser.dom_inspector import inspect_form
from browser.form_executor import fill_form
from agent.schemas import FormFillPlan


HTML = """
<form>
    <label for="name">Full Name</label>
    <input id="name" name="full_name" type="text" required>

    <label for="email">Email Address</label>
    <input id="email" name="email" type="email" required>

    <label for="country">Country</label>
    <select id="country" name="country" required>
        <option value="">Select country</option>
        <option value="india">India</option>
        <option value="usa">USA</option>
    </select>

    <label for="newsletter">Newsletter</label>
    <input id="newsletter" name="newsletter" type="checkbox">

    <label>
        <input type="radio" name="contact" value="email">
        Email
    </label>

    <label>
        <input type="radio" name="contact" value="phone">
        Phone
    </label>

    <label for="message">Message</label>
    <textarea id="message" name="message"></textarea>
</form>
"""


async def main():
    async with browser_session(headless=True) as page:

        await page.set_content(HTML)

        # Inspect actual DOM.
        form_fields = await inspect_form(page)

        # Simulate a human-approved mapping.
        approved_plan = FormFillPlan(
            mappings=[
                {
                    "field_name": "Full Name",
                    "field_key": "full_name",
                    "control_type": "text",
                    "value": "Somesh Jaiswal",
                    "reason": "User provided name.",
                },
                {
                    "field_name": "Email Address",
                    "field_key": "email",
                    "control_type": "email",
                    "value": "somesh@example.com",
                    "reason": "User provided email.",
                },
                {
                    "field_name": "Country",
                    "field_key": "country",
                    "control_type": "select",
                    "value": "india",
                    "reason": "User selected India.",
                },
                {
                    "field_name": "Newsletter",
                    "field_key": "newsletter",
                    "control_type": "checkbox",
                    "value": True,
                    "reason": "User requested subscription.",
                },
                {
                    "field_name": "Contact",
                    "field_key": "contact",
                    "control_type": "radio",
                    "value": "email",
                    "reason": "User selected email.",
                },
                {
                    "field_name": "Message",
                    "field_key": "message",
                    "control_type": "textarea",
                    "value": "Hello from WebForm Agent.",
                    "reason": "User provided message.",
                },
            ]
        )

        results = await fill_form(
            page=page,
            form_fields=form_fields,
            approved_plan=approved_plan,
        )

        print("\nEXECUTION RESULTS:")
        for field, result in results.items():
            print(field, result)

        assert all(
            result["success"] and result["verified"]
            for result in results.values()
        )

        assert await page.locator("#name").input_value() == "Somesh Jaiswal"
        assert await page.locator("#email").input_value() == "somesh@example.com"
        assert await page.locator("#country").input_value() == "india"
        assert await page.locator("#newsletter").is_checked()
        assert await page.locator(
            'input[name="contact"][value="email"]'
        ).is_checked()
        assert await page.locator("#message").input_value() == (
            "Hello from WebForm Agent."
        )

        print("\nALL SIX FIELD TYPES PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
