from agent.schemas import (
    FormField,
    FieldMapping,
    FormFillPlan
)


def main():

    # Test 1: Website field metadata
    field = FormField(
        tag="input",
        type="email",
        name="email",
        id="customer-email",
        label="Email Address",
        required=True
    )

    print("FormField:", field.model_dump())

    # Test 2: Proposed mapping
    mapping = FieldMapping(
        field_name="email",
        selector="#customer-email",
        control_type="email",
        value="somesh@example.com"
    )

    print("FieldMapping:", mapping.model_dump())

    # Test 3: Complete execution plan
    plan = FormFillPlan(
        mappings=[mapping]
    )

    print("FormFillPlan:", plan.model_dump())

    from pydantic import ValidationError

    try:
        FieldMapping(
            field_name="email",
            selector="#customer-email",
            control_type="invalid",
            value="somesh@example.com"
        )

    except ValidationError as exc:
        print("Validation correctly rejected invalid mapping")
        print(exc)



if __name__ == "__main__":
    main()