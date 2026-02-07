import google.generativeai as genai
from fastapi import HTTPException
import json
import re
from app.config import settings
from app.models.quiz import Quiz

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

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
        # Try primary model
        model_name = settings.GEMINI_MODEL
        model = genai.GenerativeModel(model_name)
        
        try:
            response = await model.generate_content_async(prompt)
            content = response.text
        except Exception as e:
            error_str = str(e)
            # If 429 (Quota) or 404 (Not Found), try fallback
            if "429" in error_str or "404" in error_str:
                print(f"DEBUG: Primary model {model_name} failed ({error_str}). Trying fallback...")
                fallback_model = "gemini-1.5-flash" if "2.0" in model_name else "gemini-pro"
                model = genai.GenerativeModel(fallback_model)
                response = await model.generate_content_async(prompt)
                content = response.text
            else:
                raise e

        # Clean up Markdown code blocks
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
        content = content.strip()
        
        quiz_data = json.loads(content)
    except Exception as e:
        print(f"DEBUG: Quiz Generation Error. Details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI model xatosi: {str(e)}")
    
    # Validate and return as Quiz model
    return Quiz(**quiz_data)


