import os

from httpx import AsyncClient

from app.ai.chat_schemas import GeminiResponse


async def handle_gemini_request(client: AsyncClient, prompt: str) -> str:
    request_payload = {"contents": [{"parts": [{"text": prompt}]}]}
    api_key = os.environ["GEMINI_API_KEY"]
    response = await client.post(
        url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        headers={"Content-type": "application/json", "x-goog-api-key": api_key},
        json=request_payload,
    )
    response.raise_for_status()
    data = GeminiResponse(**response.json())
    return data.candidates[0].content.parts[0].text.strip()
