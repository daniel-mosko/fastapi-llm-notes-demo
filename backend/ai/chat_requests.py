import os

from backend.ai.chat_schemas import GeminiResponse
from httpx import AsyncClient


async def handle_gemini_request(client: AsyncClient, prompt: str) -> str:
    request_payload = {"contents": [{"parts": [{"text": prompt}]}]}

    api_key = os.environ["GEMINI_API_KEY"]

    response = await client.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        json=request_payload,
    )

    response.raise_for_status()
    data = GeminiResponse(**response.json())
    return data.candidates[0].content.parts[0].text.strip()
