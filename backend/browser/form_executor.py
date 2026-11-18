
from playwright.async_api import Page

from agent.schemas import FormField, FormFillPlan, FieldMapping


def xpath_literal(value: str) -> str:
    """
    Safely encode a Python string as an XPath string literal.
    Handles values containing single and double quotes.
    """

    if "'" not in value:
        return f"'{value}'"

    if '"' not in value:
        return f'"{value}"'

    parts = value.split("'")
    quoted_parts = []

    for index, part in enumerate(parts):
        if part:
            quoted_parts.append(f"'{part}'")

        if index < len(parts) - 1:
            quoted_parts.append('"\'"')

    return f"concat({', '.join(quoted_parts)})"


async def resolve_field_locator(
    page: Page,
    form_fields: list[FormField],
    mapping: FieldMapping,
):
    """
    Resolve an approved logical field mapping to exactly one
    visible Playwright locator.

    The LLM never supplies CSS selectors.
    Python resolves locators using inspected DOM metadata.
    """

    matching_fields = [
        field
        for field in form_fields
        if (field.name or field.id) == mapping.field_key
        and field.type == mapping.control_type
    ]

    if not matching_fields:
        raise ValueError(
            f"Field not found: {mapping.field_key}"
        )

    # Radio buttons sharing a name form one logical field.
    if mapping.control_type == "radio":

        matching_fields = [
            field
            for field in matching_fields
            if field.choice_value == mapping.value
        ]

        if len(matching_fields) != 1:
            raise ValueError(
                f"Expected exactly one radio option with value "
                f"'{mapping.value}' for {mapping.field_key}"
            )

    else:
        if len(matching_fields) != 1:
            raise ValueError(
                f"Ambiguous field metadata for {mapping.field_key}"
            )

    field = matching_fields[0]

    # Prefer ID when available; otherwise use name.
    if field.id:
        attribute = "id"
        attribute_value = field.id
    elif field.name:
        attribute = "name"
        attribute_value = field.name
    else:
        raise ValueError(
            f"Field {mapping.field_key} has no usable identifier"
        )

    selector = (
        f"//{field.tag}"
        f"[@{attribute}={xpath_literal(attribute_value)}]"
    )

    # Radio option must match the exact approved choice.
    if mapping.control_type == "radio":
        selector += (
            f"[@value={xpath_literal(mapping.value)}]"
        )

    locator = page.locator(selector)

    count = await locator.count()

    if count != 1:
        raise ValueError(
            f"Expected exactly one DOM element for "
            f"{mapping.field_key}, found {count}"
        )

    if not await locator.is_visible():
        raise ValueError(
            f"Field is not visible: {mapping.field_key}"
        )

    if not await locator.is_enabled():
        raise ValueError(
            f"Field is disabled: {mapping.field_key}"
        )

    if await locator.get_attribute("readonly") is not None:
        raise ValueError(
            f"Field is read-only: {mapping.field_key}"
        )

    return locator


async def execute_mapping(
    locator,
    mapping: FieldMapping,
) -> None:
    """
    Execute one approved field mapping.

    This function only fills form controls.
    It never submits the form.
    """

    value = mapping.value
    control_type = mapping.control_type

    # Missing optional values should not modify the form.
    if value is None:
        return

    if control_type == "checkbox":

        if not isinstance(value, bool):
            raise ValueError(
                f"Checkbox {mapping.field_key} requires "
                "a boolean value"
            )

        await locator.set_checked(value)

    elif control_type == "radio":

        if not isinstance(value, str):
            raise ValueError(
                f"Radio {mapping.field_key} requires "
                "a string choice value"
            )

        await locator.check()

    elif control_type == "select":

        if not isinstance(value, str):
            raise ValueError(
                f"Select {mapping.field_key} requires "
                "a string choice value"
            )

        await locator.select_option(value=value)

    elif control_type in {
        "text",
        "email",
        "tel",
        "url",
        "number",
        "date",
        "password",
        "textarea",
    }:

        if not isinstance(value, str):
            raise ValueError(
                f"Field {mapping.field_key} requires "
                "a string value"
            )

        await locator.fill(value)

    else:
        raise ValueError(
            f"Unsupported control type: {control_type}"
        )


async def verify_mapping(
    locator,
    mapping: FieldMapping,
) -> bool:
    """
    Verify that Playwright successfully applied the approved value.
    """

    value = mapping.value
    control_type = mapping.control_type

    if value is None:
        return True

    if control_type == "checkbox":
        return await locator.is_checked() is value

    if control_type == "radio":
        return await locator.is_checked()

    if control_type == "select":
        selected_value = await locator.input_value()
        return selected_value == value

    actual_value = await locator.input_value()

    return actual_value == value


async def fill_form(
    page: Page,
    form_fields: list[FormField],
    approved_plan: FormFillPlan,
) -> dict:
    """
    Execute a human-approved FormFillPlan.

    Responsibilities:
    1. Resolve logical fields to browser locators.
    2. Execute approved values.
    3. Verify the resulting browser state.
    4. Return per-field execution results.

    This function never submits the form.
    """

    if not approved_plan.requires_human_approval:
        raise ValueError(
            "FormFillPlan must require human approval"
        )

    results = {}

    for mapping in approved_plan.mappings:

        field_name = mapping.field_name

        try:
            # Missing optional values are intentionally skipped.
            if mapping.value is None:
                results[field_name] = {
                    "success": True,
                    "verified": True,
                    "status": "skipped",
                    "reason": "No value provided",
                }
                continue

            # Resolve the actual browser element.
            locator = await resolve_field_locator(
                page=page,
                form_fields=form_fields,
                mapping=mapping,
            )

            # Execute the approved mapping.
            await execute_mapping(
                locator=locator,
                mapping=mapping,
            )

            # Verify the actual browser state.
            verified = await verify_mapping(
                locator=locator,
                mapping=mapping,
            )

            if not verified:
                raise ValueError(
                    f"Value verification failed for "
                    f"{mapping.field_key}"
                )

            results[field_name] = {
                "success": True,
                "verified": True,
                "status": "filled",
            }

        except Exception as exc:

            results[field_name] = {
                "success": False,
                "verified": False,
                "status": "failed",
                "error": str(exc),
            }

    return results
