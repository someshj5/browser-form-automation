
from playwright.async_api import Page

from browser.dom_inspector import inspect_form
from browser.form_executor import fill_form

from agent.nodes.field_mapper import map_form_fields
from agent.schemas import FormFillPlan, FormField


async def prepare_form_fill(
    page: Page,
    user_instruction: str,
) -> tuple[list[FormField], FormFillPlan]:
    """
    Inspect the page and generate a proposed form-filling plan.

    This function does not modify the form.
    """

    # Step 1: Inspect the actual browser DOM.
    form_fields = await inspect_form(page)

    if not form_fields:
        raise ValueError("No supported form fields detected")

    # Step 2: Generate semantic mappings using Ollama.
    plan = await map_form_fields(
        user_instruction=user_instruction,
        form_fields=form_fields,
    )

    # Step 3: Return the plan for human review.
    return form_fields, plan


async def execute_approved_fill(
    page: Page,
    form_fields: list[FormField],
    approved_plan: FormFillPlan,
    approval_confirmed: bool,
) -> dict:
    """
    Execute a plan only after explicit human approval.

    Never submits the form.
    """

    if not approval_confirmed:
        raise PermissionError(
            "Human approval is required before filling the form."
        )

    return await fill_form(
        page=page,
        form_fields=form_fields,
        approved_plan=approved_plan,
    )
