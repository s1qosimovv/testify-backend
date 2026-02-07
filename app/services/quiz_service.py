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

def store_quiz_in_memory(quiz: Quiz) -> str:
    """
    Store quiz in memory and return an ID
    For MVP, we'll use a simple in-memory dict
    In production, use Redis or database
    
    Args:
        quiz: Quiz to store
        
    Returns:
        Quiz ID
    """
    import uuid
    quiz_id = str(uuid.uuid4())
    
    # Global in-memory storage (for MVP only)
    if not hasattr(store_quiz_in_memory, 'storage'):
        store_quiz_in_memory.storage = {}
    
    store_quiz_in_memory.storage[quiz_id] = quiz
    return quiz_id

def get_quiz_from_memory(quiz_id: str) -> Quiz:
    """
    Retrieve quiz from memory by ID
    
    Args:
        quiz_id: Quiz identifier
        
    Returns:
        Quiz object
        
    Raises:
        HTTPException: If quiz not found
    """
    if not hasattr(store_quiz_in_memory, 'storage'):
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz = store_quiz_in_memory.storage.get(quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quiz
