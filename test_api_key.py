"""
Gemini API kalitni tekshirish scripti
Bu script yangi API kalit ishlayotganini tekshiradi
"""
import google.generativeai as genai
import sys

# MUHIM: Bu faylni GitHub'ga push qilishdan oldin API kalitni o'chiring!
# Render'da environment variable ishlatiladi
API_KEY = "YOUR_API_KEY_HERE"  # Bu yerga test uchun vaqtinchalik kalit qo'ying

print("🔍 Gemini API kalitni tekshiryapman...")
print(f"API Kalit: {API_KEY[:20] if len(API_KEY) > 20 else 'NOT_SET'}...")

if API_KEY == "YOUR_API_KEY_HERE":
    print("\n❌ XATOLIK: API kalit o'rnatilmagan!")
    print("💡 Scriptni tahrirlang va API_KEY o'zgaruvchisiga kalitni qo'ying")
    sys.exit(1)

try:
    genai.configure(api_key=API_KEY)
    
    # Test 1: Oddiy so'rov
    print("\n📝 Test 1: Oddiy matn generatsiyasi...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Salom! Bu test xabari. Qisqa javob ber.")
    
    print("✅ API kalit ISHLAYAPTI!")
    print(f"📨 Javob: {response.text[:100]}...")
    
    # Test 2: Quiz generatsiya testi
    print("\n📝 Test 2: Quiz generatsiya testi...")
    quiz_prompt = """Sen professional test tuzuvchisan.
    
Quyidagi matn asosida 2 ta savol tuz (JSON formatda):

MATN: Python - bu dasturlash tili.

JSON FORMAT:
{
  "quiz": [
    {
      "question": "Savol matni",
      "options": {
        "A": "Variant A",
        "B": "Variant B",
        "C": "Variant C",
        "D": "Variant D"
      },
      "correct_answer": "A"
    }
  ]
}
"""
    
    response2 = model.generate_content(quiz_prompt)
    print("✅ Quiz generatsiya ham ISHLAYAPTI!")
    print(f"📨 Javob: {response2.text[:200]}...")
    
    print("\n" + "="*50)
    print("🎉 HAMMASI ISHLAYAPTI!")
    print("="*50)
    print("\n💡 Agar bu yerda ishlasa, lekin Render'da ishlamasa:")
    print("   1. Render'da 'Clear build cache & deploy' qiling")
    print("   2. Environment variable to'g'ri kiritilganini tekshiring")
    print("   3. Render logs'ni tekshiring")
    
except Exception as e:
    error_msg = str(e)
    print("\n" + "="*50)
    print("❌ XATOLIK YUZAGA KELDI!")
    print("="*50)
    print(f"Xatolik: {error_msg}\n")
    
    if "429" in error_msg or "quota" in error_msg.lower():
        print("🚨 MUAMMO: API limiti tugagan!")
        print("\n💡 Yechimlar:")
        print("   1. Yangi Google akkaunt yarating")
        print("   2. Yangi akkaunt bilan yangi API kalit oling")
        print("   3. Yoki 24 soat kuting (kunlik limit qayta tiklanadi)")
    elif "API key" in error_msg or "invalid" in error_msg.lower():
        print("🚨 MUAMMO: API kalit noto'g'ri!")
        print("\n💡 Yechimlar:")
        print("   1. Google AI Studio'da yangi kalit yarating")
        print("   2. Kalitni to'g'ri nusxalganingizni tekshiring")
        print("   3. Bo'sh joy yoki qo'shimcha belgi yo'qligini tekshiring")
    else:
        print("🚨 MUAMMO: Noma'lum xatolik!")
        print("\n💡 Yechimlar:")
        print("   1. Internet aloqangizni tekshiring")
        print("   2. Firewall yoki antivirus to'sib qo'ygan bo'lishi mumkin")
        print("   3. VPN ishlatib ko'ring")
    
    sys.exit(1)
