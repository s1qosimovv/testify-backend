import google.generativeai as genai
from fastapi import HTTPException
import json
import re
from app.config import settings
from app.models.quiz import Quiz

# Configure Gemini API
genai.configure(api_key=settings.OPENAI_API_KEY)

async def generate_quiz(text: str, num_questions: int = 10) -> Quiz:
    """
    Generate quiz questions from text using Google Gemini API
    
    Args:
        text: Input text to generate quiz from
        num_questions: Number of questions to generate (default: 10)
        
    Returns:
        Quiz object with generated questions
        
    Raises:
        HTTPException: If API call fails or response is invalid
    """
    
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured"
        )
    
    # Create production-ready prompt for quiz generation
    prompt = f"""Sen professional o'qituvchi va test tuzuvchi sun'iy intellektsan.

Vazifa:
Quyidagi matn asosida quiz tuz.

QOIDALAR:
- Savollar soni: {num_questions} ta
- Har bir savolda 4 ta variant bo'lsin (A, B, C, D)
- Faqat BITTA to'g'ri javob bo'lsin
- Savollar matn mazmuniga to'liq mos bo'lsin
- Savollar o'zbek tilida bo'lsin
- Savollar aniq, qisqa va tushunarli bo'lsin
- Variantlar bir-biriga juda o'xshash bo'lmasin

QATTIQ TEXNIK TALABLAR:
- Javob FAQAT JSON formatda bo'lsin
- Hech qanday izoh, tushuntirish yoki qo'shimcha matn yozma
- Markdown ishlatma (```json ... ``` kabi belgilarsiz toza JSON bo'lsin)
- JSON strukturani o'zgartirma
- Agar matn yetarli bo'lmasa, umumiy mazmunga mos savollar tuz

JSON FORMAT (ANIQ SHU KO'RINISHDA):
{{
  "quiz": [
    {{
      "question": "Savol matni",
      "options": {{
        "A": "Variant A",
        "B": "Variant B",
        "C": "Variant C",
        "D": "Variant D"
      }},
      "correct_answer": "A"
    }}
  ]
}}

MATN:
{text[:4000]}
"""
    
    # Initialize model
    model = genai.GenerativeModel(settings.OPENAI_MODEL)
    
    # Generate content
    response = model.generate_content(prompt)
    content = response.text
    
    # Clean up Markdown code blocks if present
    if "```json" in content:
        content = content.replace("```json", "").replace("```", "")
    elif "```" in content:
        content = content.replace("```", "")
        
    content = content.strip()
    
    # Parse JSON
    try:
        quiz_data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON Decode Error. Content was: {content}")
        raise e
    
    # Validate and return as Quiz model
    return Quiz(**quiz_data)


