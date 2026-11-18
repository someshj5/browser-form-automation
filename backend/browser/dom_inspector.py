
from agent.schemas import *

async def inspect_form(page):
    """
    Inspect visible form controls and return structured metadata.
    """

    fields = page.locator(
        "input, textarea, select"
    )

    metadata = await fields.evaluate_all("""
        elements => elements
            .filter(el => {
                const style = window.getComputedStyle(el);

                return (
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    el.type !== "hidden"
                );
            })
            .map(el => {

                const tag = el.tagName.toLowerCase();

                return {
                    tag: tag,
                    type: tag === "input" ? el.type : tag,

                    name: el.name,
                    id: el.id,

                    label: (() => {
                    const associated = Array.from(el.labels || [])
                        .map(label => label.innerText.trim())
                        .filter(Boolean)
                        .join(" ");

                    if (associated) return associated;

                    const ariaLabel = el.getAttribute("aria-label");
                    if (ariaLabel) return ariaLabel.trim();

                    const labelledBy = el.getAttribute("aria-labelledby");

                    if (labelledBy) {
                        return labelledBy
                            .split(" ")
                            .map(id => document.getElementById(id)?.innerText || "")
                            .filter(Boolean)
                            .join(" ")
                            .trim();
                    }

                    return (
                        el.getAttribute("placeholder") ||
                        el.getAttribute("name") ||
                        el.id ||
                        ""
                    );
                })(),

                    placeholder: el.placeholder || null,

                    required: el.required,
                    disabled: el.disabled,

                    choice_value: (
                        el.type === "radio" || el.type === "checkbox"
                    ) ? el.value : null,

                    checked: (
                        tag === "input" &&
                        ["checkbox", "radio"].includes(el.type)
                    ) ? el.checked : null,

                 

                    options: tag === "select"
                        ? Array.from(el.options).map(option => ({
                            label: option.label,
                            value: option.value,
                            disabled: option.disabled
                        }))
                        : []
                };
            });
    """)

    return [
    FormField.model_validate(field)
    for field in metadata
]
