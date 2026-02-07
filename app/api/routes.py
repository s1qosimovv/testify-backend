from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_reader import extract_text
from app.services.ai_service import generate_quiz
from app.services.quiz_service import evaluate_answers, store_quiz_in_memory, get_quiz_from_memory
from app.models.quiz import TextInput, Quiz, AnswerSubmission, QuizResult

router = APIRouter()

@router.post("/upload-file", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """
    Extract text from uploaded file (PDF, DOCX, or TXT)
    """
    text = await extract_text(file)
    
    if not text or len(text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Faylda o'qiladigan matn topilmadi. Iltimos, boshqa fayl yuklang."
        )
    
    return {"text": text}

@router.post("/generate-quiz", response_model=dict)
async def create_quiz(input_data: TextInput):
    """
    Generate quiz from provided text using AI
    Returns quiz with a unique ID
    """
    if not input_data.text or len(input_data.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Text is too short. Please provide at least 50 characters."
        )
    
    # Generate quiz using AI
    try:
        quiz = await generate_quiz(input_data.text, num_questions=input_data.num_questions)
    except Exception as e:
        print(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Store quiz and get ID
    quiz_id = store_quiz_in_memory(quiz)
    
    return {
        "quiz_id": quiz_id,
        "quiz": quiz.dict()
    }

@router.post("/submit-answers", response_model=QuizResult)
async def submit_answers(quiz_id: str, submission: AnswerSubmission):
    """
    Evaluate user's answers and return score
    """
    # Retrieve the quiz
    quiz = get_quiz_from_memory(quiz_id)
    
    # Evaluate answers
    result = evaluate_answers(quiz, submission)
    
    return result
@router.post("/get-telegram-link", response_model=dict)
async def get_telegram_link(quiz_id: str):
    """
    Generate a deep link to the Telegram bot for this quiz
    """
    from app.config import settings
    import os
    
    bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "TestifyHub_bot")
    # Using startgroup instead of start to allow adding to groups
    share_link = f"https://t.me/{bot_username}?startgroup=q_{quiz_id}"
    
    return {"share_link": share_link}
