import asyncio

from agent.nodes.field_mapper import map_form_fields
from agent.schemas import FormField
import pytest

from agent.nodes.field_mapper import (
    prepare_form_context,
    validate_plan,
)
from agent.schemas import FormFillPlan


async def main():

    form_fields = [
        FormField(
            tag="input",
            type="text",
            name="full_name",
            id="name",
            label="Full Name",
            required=True,
        ),
        FormField(
            tag="input",
            type="email",
            name="email",
            id="email",
            label="Email Address",
            required=True,
        ),
        FormField(
            tag="select",
            type="select",
            name="country",
            id="country",
            label="Country",
            required=True,
            options=[
                {"label": "Select country", "value": "", "disabled": False},
                {"label": "India", "value": "india", "disabled": False},
                {"label": "USA", "value": "usa", "disabled": False},
            ],
        ),
        FormField(
            tag="input",
            type="checkbox",
            name="newsletter",
            id="newsletter",
            label="Subscribe to newsletter",
            checked=False,
            choice_value="on",
        ),
        FormField(
            tag="input",
            type="radio",
            name="contact",
            label="Email",
            checked=False,
            choice_value="email",
        ),
        FormField(
            tag="input",
            type="radio",
            name="contact",
            label="Phone",
            checked=False,
            choice_value="phone",
        ),
        FormField(
            tag="textarea",
            type="textarea",
            name="message",
            label="Message",
        ),
    ]

    instruction = """
    Fill my name as Somesh Jaiswal.
    My email is somesh@example.com.
    Select India as my country.
    Subscribe to the newsletter.
    Choose Email as my preferred contact method.
    """

    plan = await map_form_fields(
        user_instruction=instruction,
        form_fields=form_fields,
    )

    print("\nGenerated FormFillPlan:\n")
    print(plan.model_dump_json(indent=2))

    print("\nField mapping test passed!")

def test_rejects_missing_required_email():

    form_fields = [
        FormField(
            tag="input",
            type="email",
            name="email",
            id="email",
            label="Email Address",
            required=True,
        )
    ]

    form_context = prepare_form_context(form_fields)

    invalid_plan = FormFillPlan(
        mappings=[
            {
                "field_name": "Email Address",
                "field_key": "email",
                "control_type": "email",
                "value": None,
                "reason": "User did not provide an email.",
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="Required field",
    ):
        validate_plan(invalid_plan, form_context)

    print("Missing required email correctly rejected!")

def test_rejects_whitespace_required_email():

    form_fields = [
        FormField(
            tag="input",
            type="email",
            name="email",
            id="email",
            label="Email Address",
            required=True,
        )
    ]

    form_context = prepare_form_context(form_fields)

    invalid_plan = FormFillPlan(
        mappings=[
            {
                "field_name": "Email Address",
                "field_key": "email",
                "control_type": "email",
                "value": "   ",
                "reason": "Whitespace-only value.",
            }
        ]
    )

    with pytest.raises(ValueError, match="Required field"):
        validate_plan(invalid_plan, form_context)

    print("Whitespace-only required email correctly rejected!")


def test_rejects_invalid_email_format():
    form_fields = [
        FormField(
            tag="input",
            type="email",
            name="email",
            id="email",
            label="Email Address",
            required=True,
        )
    ]

    form_context = prepare_form_context(form_fields)

    invalid_plan = FormFillPlan(
        mappings=[
            {
                "field_name": "Email Address",
                "field_key": "email",
                "control_type": "email",
                "value": "somesh@",
                "reason": "Invalid email supplied.",
            }
        ]
    )

    with pytest.raises(ValueError, match="Invalid email format"):
        validate_plan(invalid_plan, form_context)

    print("Invalid email format correctly rejected!")

def test_checkbox_false_is_valid():

    form_fields = [
        FormField(
            tag="input",
            type="checkbox",
            name="newsletter",
            id="newsletter",
            label="Subscribe to newsletter",
            required=False,
        )
    ]

    form_context = prepare_form_context(form_fields)

    plan = FormFillPlan(
        mappings=[
            {
                "field_name": "Subscribe to newsletter",
                "field_key": "newsletter",
                "control_type": "checkbox",
                "value": False,
                "reason": "User explicitly declined subscription.",
            }
        ]
    )

    validated_plan = validate_plan(plan, form_context)

    assert validated_plan.mappings[0].value is False

    print("Checkbox False correctly accepted!")

if __name__ == "__main__":
    asyncio.run(main())
    test_rejects_missing_required_email()
    test_rejects_whitespace_required_email()
    test_rejects_invalid_email_format()
    test_checkbox_false_is_valid()