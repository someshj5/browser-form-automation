import asyncio

from agent.ollama_client import OllamaClient


async def main():
    client = OllamaClient()

    prompt = """
    Return a JSON object with exactly two keys:
    - name: "Somesh Jaiswal"
    - email: "somesh@example.com"

    Return only valid JSON.
    """

    result = await client.generate_json(prompt)

    print("Ollama response:", result)

    assert isinstance(result, dict)
    assert result["name"] == "Somesh Jaiswal"
    assert result["email"] == "somesh@example.com"

    print("Ollama inference test passed!")


if __name__ == "__main__":
    asyncio.run(main())