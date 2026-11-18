import json

from ollama import AsyncClient
import re
import yaml

class OllamaClient:
    def __init__(
        self,
        model: str = "llama3.2:3b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.client = AsyncClient(host=host)

    async def generate_yaml(self, prompt: str) -> dict:
        response = await self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
            },
        )

        content = response.message.content.strip()

        # Remove Markdown YAML code fences, if present.
        content = re.sub(
            r"^```(?:yaml|yml)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise ValueError(
                f"Ollama returned invalid YAML: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "Expected a YAML mapping from Ollama"
            )

        return data

    async def generate_json(
        self,
        prompt: str,
        schema: dict | None = None,
    ) -> dict:

        response = await self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format=schema if schema else "json",
            options={
                "temperature": 0,
            },
        )

        content = response.message.content

        return json.loads(content)