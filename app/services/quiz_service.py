from app.models.quiz import Quiz, AnswerSubmission, QuizResult
from fastapi import HTTPException

def evaluate_answers(quiz: Quiz, submission: AnswerSubmission) -> QuizResult:
    """
    Evaluate user's answers against correct answers
    
    Args:
        quiz: The original quiz with correct answers
        submission: User's submitted answers
        
    Returns:
        QuizResult with score, total, and percentage
        
    Raises:
        HTTPException: If submission is invalid
    """
    
    total = len(quiz.quiz)
    score = 0
    
    # Check each answer
    for idx, question in enumerate(quiz.quiz):
        user_answer = submission.answers.get(idx)
        
        if user_answer and user_answer == question.correct_answer:
            score += 1
    
    # Calculate percentage
    percentage = round((score / total) * 100, 2) if total > 0 else 0
    
    return QuizResult(
        score=score,
        total=total,
        percentage=percentage
    )

import json
import os
import uuid

# Storage path
STORAGE_FILE = "quizzes.json"

def _load_storage():
    """Load storage from file"""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_storage(data):
    """Save storage to file"""
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def store_quiz_in_memory(quiz: Quiz) -> str:
    """
    Store quiz in a file to survive reloads
    """
    quiz_id = str(uuid.uuid4())
    storage = _load_storage()
    storage[quiz_id] = quiz.dict()
    _save_storage(storage)
    return quiz_id

def get_quiz_from_memory(quiz_id: str) -> Quiz:
    """
    Retrieve quiz from file by ID
    """
    storage = _load_storage()
    quiz_data = storage.get(quiz_id)
    
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return Quiz(**quiz_data)
