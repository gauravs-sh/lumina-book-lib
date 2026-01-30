from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    excerpts: list[str]


class SummaryRequest(BaseModel):
    content: str
