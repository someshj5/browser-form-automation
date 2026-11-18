
import asyncio

from browser.session import browser_session
from agent.runner import (
    prepare_form_fill,
    execute_approved_fill,
)


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

    async with browser_session(headless=False) as page:

        await page.set_content(HTML)

        instruction = """
        Fill my name as Somesh Jaiswal.
        My email is somesh@example.com.
        Select India as my country.
        Subscribe to the newsletter.
        Choose Email as my preferred contact method.
        """

        # Phase 1: Inspect and generate a proposed plan.
        form_fields, proposed_plan = await prepare_form_fill(
            page=page,
            user_instruction=instruction,
        )

        print("\nPROPOSED PLAN:")
        print(proposed_plan.model_dump_json(indent=2))

        # Phase 2: Simulate explicit human approval.
        # In the real application, this comes from the frontend.
        approval_confirmed = True

        results = await execute_approved_fill(
            page=page,
            form_fields=form_fields,
            approved_plan=proposed_plan,
            approval_confirmed=approval_confirmed,
        )
        input("Press Enter to close the browser...")

        print("\nEXECUTION RESULTS:")
        for field, result in results.items():
            print(field, result)

        assert all(
            result["success"] and result["verified"]
            for result in results.values()
        )

        print("\nEND-TO-END AGENT TEST PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
