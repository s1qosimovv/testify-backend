from pydantic import BaseModel
from typing import Dict, List

class Question(BaseModel):
    """Single quiz question model"""
    question: str
    options: Dict[str, str]  # {"A": "option1", "B": "option2", ...}
    correct_answer: str  # "A", "B", "C", or "D"

class Quiz(BaseModel):
    """Complete quiz model"""
    title: str = "AI Quiz"
    description: str = ""
    quiz: List[Question]

class TextInput(BaseModel):
    """Input model for text-based quiz generation"""
    text: str
    num_questions: int = 10

class AnswerSubmission(BaseModel):
    """User's answers submission"""
    answers: Dict[int, str]  # {0: "A", 1: "C", 2: "B"}

class QuizResult(BaseModel):
    """Quiz result after evaluation"""
    score: int
    total: int
    percentage: float
