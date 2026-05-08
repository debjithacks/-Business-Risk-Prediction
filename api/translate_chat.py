import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def translate_to_bengali(text):

    try:

        prompt = f"""
You are a professional English to Bengali translator.

Translate the following English text into FULL Bengali.

IMPORTANT RULES:

1. Translate COMPLETE sentences.
2. Do NOT skip any words.
3. Do NOT leave English words.
4. Use natural Bengali language.
5. Keep original meaning exactly same.
6. Do NOT shorten the sentence.
7. Return FULL Bengali translation only.
8. Do NOT explain anything.
9. Do NOT add headings.
10. Make sure translation is COMPLETE.

Text:
{text}
"""

        response = client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            # 🔥 Better translation model
            model="llama-3.3-70b-versatile",

            temperature=0.1,

            max_tokens=600

        )

        bengali_text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return bengali_text

    except Exception as e:

        print("TRANSLATION ERROR:", e)

        return "বাংলা অনুবাদ সম্পূর্ণ করা যায়নি।"