import os

from fastapi import HTTPException, status
from httpx import AsyncClient


async def handle_gemini_request(client: AsyncClient, prompt: str) -> str:
    api_key = os.environ["GEMINI_API_KEY"]

    response = await client.post(
        url="https://generativelanguage.googleapis.com/v1beta/interactions",
        headers={"Content-type": "application/json", "x-goog-api-key": api_key},
        json={
            "model": "gemini-3-flash-preview",
            "input": prompt,
        },
        timeout=15.0,
    )

    response.raise_for_status()
    data = response.json()

    # Extract text from the last output
    if data.get("outputs"):
        return data["outputs"][-1]["text"]

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to parse output from Gemini request",
    )
