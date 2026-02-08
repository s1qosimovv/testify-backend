import google.generativeai as genai
from fastapi import HTTPException
import asyncio
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
        # Try a list of models in order of preference for speed and rate limits
        # gemini-1.5-flash is usually the fastest and most stable for free tier
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
        
        # If user has a specific model in settings, try it first
        if settings.GEMINI_MODEL and settings.GEMINI_MODEL not in models_to_try:
            models_to_try.insert(0, settings.GEMINI_MODEL)
            
        content = None
        last_error = ""
        is_rate_limit = False
        
        # Get available keys
        api_keys = settings.GEMINI_API_KEYS
        if not api_keys:
             raise HTTPException(status_code=500, detail="API keys not configured")

        # Try each API Key
        for key_index, api_key in enumerate(api_keys):
            print(f"DEBUG: Using API Key #{key_index + 1} ({api_key[:5]}...)")
            genai.configure(api_key=api_key)
            
            # Try models with this key
            for model_name in models_to_try:
                # For each model, try up to 2 times with backoff
                for attempt in range(2):
                    try:
                        print(f"DEBUG: [Key #{key_index+1}] Trying {model_name} (Attempt {attempt + 1})...")
                        model = genai.GenerativeModel(model_name)
                        # Set generation config to ensure JSON response
                        generation_config = genai.GenerationConfig(
                            response_mime_type="application/json"
                        )
                        
                        response = await model.generate_content_async(
                            prompt, 
                            generation_config=generation_config
                        )
                        content = response.text
                        if content:
                            print(f"DEBUG: Success with {model_name} on Key #{key_index+1}")
                            break
                    except Exception as e:
                        last_error = str(e)
                        print(f"DEBUG: [Key #{key_index+1}] Model {model_name} attempt {attempt+1} failed: {last_error}")
                        
                        if "429" in last_error or "quota" in last_error.lower() or "resource" in last_error.lower():
                            is_rate_limit = True
                            # If we have more keys, break model loop and switch key immediately
                            if key_index < len(api_keys) - 1:
                                print(f"DEBUG: Key #{key_index+1} exhausted. Switching to next key...")
                                break # Break model loop, continue to next key
                            
                            # If no more keys, wait and retry current key
                            wait_time = 2 ** (attempt + 1)
                            print(f"DEBUG: Rate limit on final key. Waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                        else:
                            # If it's not a rate limit (e.g. model not found), switch to next model immediately
                            break
                
                if content: break # Break model loop
                if is_rate_limit and key_index < len(api_keys) - 1: break # Break model loop to switch key

            if content: break # Break key loop

        if not content:
            if is_rate_limit:
                raise HTTPException(
                    status_code=429, 
                    detail="⚠️ Barcha serverlar band (Kunlik limit tugadi). Iltimos, ertaga urinib ko'ring yoki developer bilan bog'laning."
                )
            raise HTTPException(status_code=500, detail=f"AI xatosi: {last_error[:100]}")

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


