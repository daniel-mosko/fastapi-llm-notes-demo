from typing import List

from pydantic import BaseModel


class GeminiPart(BaseModel):
    text: str


class GeminiContent(BaseModel):
    parts: List[GeminiPart]


class GeminiCandidate(BaseModel):
    content: GeminiContent


class GeminiResponse(BaseModel):
    candidates: List[GeminiCandidate]


class OpenAIChatMessage(BaseModel):
    content: str


class OpenAIChatChoice(BaseModel):
    message: OpenAIChatMessage


class OpenAIResponse(BaseModel):
    choices: List[OpenAIChatChoice]
