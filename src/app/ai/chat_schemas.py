from pydantic import BaseModel


class GeminiPart(BaseModel):
    text: str


class GeminiContent(BaseModel):
    parts: list[GeminiPart]


class GeminiCandidate(BaseModel):
    content: GeminiContent


class GeminiResponse(BaseModel):
    candidates: list[GeminiCandidate]


class OpenAIChatMessage(BaseModel):
    content: str


class OpenAIChatChoice(BaseModel):
    message: OpenAIChatMessage


class OpenAIResponse(BaseModel):
    choices: list[OpenAIChatChoice]
