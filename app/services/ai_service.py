import google.generativeai as genai
from fastapi import HTTPException
import json
import re
from app.config import settings
from app.models.quiz import Quiz

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_quiz(text: str, num_questions: int = 10, time_per_question: int = 30) -> Quiz:
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
    
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured (GEMINI_API_KEY)"
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
    
    # Parse JSON
    try:
        # Try a list of models in order of preference
        models_to_try = [settings.GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        content = None
        last_error = ""
        is_rate_limit = False

        for model_name in models_to_try:
            if not model_name: continue
            try:
                print(f"DEBUG: Attempting with {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = await model.generate_content_async(prompt)
                content = response.text
                if content:
                    print(f"DEBUG: Success with {model_name}")
                    break
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: Model {model_name} failed: {last_error}")
                if "429" in last_error or "quota" in last_error.lower():
                    is_rate_limit = True
                    # If it's a rate limit, don't spam other models immediately,
                    # but maybe the next one in the list has a separate quota.
                    await asyncio.sleep(1) 
                continue
        
        if not content:
            if is_rate_limit:
                raise HTTPException(
                    status_code=429, 
                    detail="Gemini AI limiti tugadi (Free Tier). Iltimos, 1 daqiqa kuting yoki boshqa matn yuboring. ⏳"
                )
            raise HTTPException(status_code=500, detail=f"AI band: {last_error[:100]}")

        # Clean up Markdown code blocks
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
        content = content.strip()
        
        quiz_data = json.loads(content)
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Quiz Generation Error. Details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI model xatosi: {str(e)}")
    
    # Validate and return as Quiz model
    quiz = Quiz(**quiz_data)
    quiz.time_per_question = time_per_question
    return quiz


