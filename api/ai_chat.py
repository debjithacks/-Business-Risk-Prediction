import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Load Groq API key
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def generate_ai_response(
    message,
    prediction,
    graph_data,
    profit=None   # ✅ ADDED (safe change)
):

    try:

        prompt = f"""
You are a professional Business Risk Assistant.

User Question:
{message}

Business Risk Data:
Overall Risk: {prediction.get("overall_risk")}
Financial Risk: {prediction.get("financial_risk")}
Operational Risk: {prediction.get("operational_risk")}
Environmental Risk: {prediction.get("environmental_risk")}
Behavioral Risk: {prediction.get("behavioral_risk")}

Latest Profit: {profit if profit is not None else "N/A"}   # ✅ ADDED

Graph Insights:
Highest Month: {graph_data.get("highest_month") if graph_data else "N/A"}
Lowest Month: {graph_data.get("lowest_month") if graph_data else "N/A"}
Trend Value: {graph_data.get("trend") if graph_data else "N/A"}

IMPORTANT KNOWLEDGE:

Profit is calculated as:

Profit = Sales - Expenses

If Latest Profit value is available:

- Always explain what the profit means for the business.
- Tell whether the profit is good, average, or low.
- Give practical business meaning instead of formula explanation.
- Do NOT explain how to calculate profit if profit already exists.
- Focus on business interpretation, not theory.

IMPORTANT RULES:

1. Give MEDIUM length answers that are easy to understand.
2. Use SIMPLE ENGLISH words used in daily life.
3. Always use NUMBERED points (1., 2., 3., etc.).
4. Give 4 to 6 numbered points when giving suggestions.
5. Each numbered point must have ONE short explanation sentence.
6. DO NOT use symbols like *, -, or bullet marks.
7. Give practical business advice based on the data.
8. Keep response length between 5 to 10 lines.
9. Avoid long paragraphs.
10. Make answers clear for beginners to understand.
11. Do NOT number heading lines.
12. Only number actual suggestion points.
13. Use profit logic correctly when user asks about profit.
14. Do NOT explain risks when question is about profit.
15. Mention Latest Profit ONLY when the user question is directly about profit.
16. If the user question is about sales, do NOT mention profit unless specifically asked.

Answer now:
"""

        chat_completion = client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=180

        )

        response_text = chat_completion.choices[0].message.content

        # -------------------------------
        # CLEAN RESPONSE FORMATTING
        # -------------------------------

        response_text = response_text.replace("*", "")
        response_text = response_text.replace("-", "")

        lines = response_text.split("\n")

        formatted_lines = []

        count = 1

        for i, line in enumerate(lines):

            clean_line = line.strip()

            if not clean_line:
                continue

            clean_line = clean_line.replace("*", "")
            clean_line = clean_line.replace("-", "")

            # If already numbered → keep
            if clean_line[0].isdigit():

                formatted_lines.append(clean_line)

            # FIRST line → treat as heading
            elif i == 0:

                # Remove trailing comma from heading
                clean_line = clean_line.rstrip(",")

                formatted_lines.append(clean_line)

            # If line ends with ":" → heading
            elif clean_line.endswith(":"):

                formatted_lines.append(clean_line)

            # Otherwise → numbered suggestion
            else:

                formatted_lines.append(
                    f"{count}. {clean_line}"
                )

                count += 1

        response_text = "\n".join(formatted_lines)

        return response_text

    except Exception as e:

        print("GROQ ERROR:", e)

        return (
            "AI response failed. Check terminal."
        )