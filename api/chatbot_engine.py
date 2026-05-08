from prediction import cumulative_prediction
from sentiment_chat import detect_chat_sentiment
from graph_chat import analyze_user_graph
from ai_chat import generate_ai_response
from prediction import generate_risk_history


# =========================
# NEW: BUSINESS FILTER FUNCTION
# =========================

def is_business_related(message: str):

    message = message.lower()

    business_keywords = [

        "risk",
        "profit",
        "loss",
        "sales",
        "revenue",
        "expense",
        "business",
        "customer",
        "finance",
        "financial",
        "operational",
        "environmental",
        "behavioral",
        "trend",
        "graph",
        "month",
        "improve",
        "growth",
        "performance",
        "cost",
        "income",
        "strategy",
        "marketing",
        "warning",
        "alert",
        "danger",
        "issue",
        "problem",
        "weakness",
        "weak",
        "improvement",
        "improve area",
        "problem area",
        "compare",
        "comparison",
        "versus",
        "vs",
        "between"

    ]

    for word in business_keywords:

        if word in message:
            return True

    return False

# =========================
# FRIENDLY STYLE DETECTOR
# =========================

def detect_friendly_style(message: str):

    message = message.lower()

    friendly_words = [

        "bro",
        "buddy",
        "boss",
        "friend",
        "hey",
        "hi bro",
        "yo",
        "bhai"

    ]

    for word in friendly_words:

        if word in message:
            return True

    return False


async def generate_chat_response(user_id: str, message: str):
    message_lower = message.lower()

    # =========================
    # STRONG GREETING HANDLER
    # =========================

    # =========================
    # FIXED GREETING HANDLER (WORD BASED)
    # =========================

    words = message_lower.split()

    # Greeting (only if short message)
    if len(words) <= 2 and any(word in ["hi", "hello", "hey"] for word in words):
        return "Hey! 👋 How can I help you with your business today?"

    # Thanks (only if short message)
    if len(words) <= 3 and any(word in ["thanks", "thank", "thx"] for word in words):
        return "You're welcome! 😊 Let me know if you need any help with your business."

    # Casual "bro" only
    if message_lower.strip() == "bro":
        return "Hey bro! 👋 Tell me what's going on with your business."

    # Friendly casual only (bro without business)
    if "bro" in message_lower and not is_business_related(message):
        return "Hey bro! 👋 Tell me what's going on with your business."

    # Allow greetings

    # =========================
    # ALLOW GREETINGS + CASUAL CHAT
    # =========================

    greetings = [
        "hi", "hello", "hey", "bro",
        "thanks", "thank you",
        "good morning", "good evening"
    ]

    if not is_business_related(message):

        # Allow casual/friendly chat
        if any(word in message_lower for word in [
            "hi", "hello", "hey", "bro",
            "thanks", "thank you"
        ]):
            pass  # allow

        else:
            return (
                "This question is not related to business. "
                "Please ask questions related to business risk, profit, sales, or improvement."
            )

    # =========================
    # Detect Sentiment
    # =========================

    sentiment = detect_chat_sentiment(message)
    # =========================
    # ENHANCED SENTIMENT DETECTION
    # =========================

    negative_words = [
        "worried", "fear", "problem", "issue",
        "loss", "bad", "failing", "stress",
        "trouble", "decline"
    ]

    is_negative = (
            sentiment == "negative"
            or any(word in message_lower for word in negative_words)
    )
    friendly_mode = "bro" in message_lower

    # =========================
    # Get Latest Prediction
    # =========================

    try:
        prediction = await cumulative_prediction(user_id)

    except Exception:
        prediction = {}

    # =========================
    # Get REAL Graph Data
    # =========================

    try:
        graph_data = await analyze_user_graph(user_id)

    except Exception:
        graph_data = None

    # =========================
    # FINAL FIX: HIGHEST SALES MONTH
    # =========================

    if (
        "highest" in message_lower
        and "sales" in message_lower
    ):

        if graph_data:

            highest_month = graph_data.get("highest_month")

            if highest_month:

                return (
                    f"The highest sales month is {highest_month}."
                )

        return "Sales data not available."

    # =========================
    # BEST PERFORMING MONTH
    # =========================

    elif (
            "best performing month" in message_lower
            or "best month" in message_lower
    ):

        if graph_data:

            best_month = graph_data.get("highest_month")

            if best_month:
                return (
                    f"The best performing month is {best_month}."
                )

        return "Best performing month data not available."

    # =========================
    # MONTH COMPARISON SYSTEM
    # =========================

    elif "compare" in message_lower:

        try:

            words = message.replace(",", "").split()

            months_found = []

            # Try to detect month names inside message
            history_data = await generate_risk_history(user_id)

            if history_data:

                available_months = history_data["months"]

                for m in available_months:

                    if m.lower() in message_lower:

                        if m not in months_found:
                            months_found.append(m)

            if len(months_found) >= 2:

                m1 = months_found[0]
                m2 = months_found[1]

                from graph_chat import compare_two_months

                result = await compare_two_months(
                    user_id,
                    m1,
                    m2
                )

                if result:

                    r1 = result["risk1"]
                    r2 = result["risk2"]

                    difference = abs(r2 - r1)

                    if r2 > r1:

                        comparison = (
                            f"{m2} had higher risk than {m1}, "
                            f"risk increased by {round(difference, 2)} points."
                        )

                    elif r2 < r1:

                        comparison = (
                            f"{m2} had lower risk than {m1}, "
                            f"risk decreased by {round(difference, 2)} points."
                        )

                    else:

                        comparison = (
                            f"{m1} and {m2} had similar risk levels."
                        )

                    return (
                        "Month comparison:\n"
                        f"1. {comparison}\n"
                        "2. Risk levels changed between months.\n"
                        "3. Performance difference is visible.\n"
                        "4. Analyze stronger month strategies.\n"
                        "5. Continue monitoring monthly performance."
                    )

            return "Please provide two valid months to compare."

        except Exception:

            return "Unable to compare the selected months."

    # =========================
    # MOST RISKY MONTHS
    # =========================

    elif (
        "most risky months" in message_lower
        or "top risky months" in message_lower
        or "highest risk months" in message_lower
    ):

        try:

            from prediction import generate_risk_history

            history_data = await generate_risk_history(user_id)

            if history_data:

                months = history_data["months"]
                risks = history_data["overall"]

                combined = list(zip(months, risks))

                # Sort highest risk first
                combined.sort(
                    key=lambda x: x[1],
                    reverse=True
                )

                top_months = combined[:3]

                response_lines = [
                    "Most risky months:"
                ]

                count = 1

                for m, r in top_months:

                    response_lines.append(
                        f"{count}. {m} – {round(r,2)}"
                    )

                    count += 1

                return "\n".join(response_lines)

            return "Risk history data not available."

        except Exception:

            return "Unable to fetch risky months data."

    response = "I'm here to help you understand your business risk."

    # =========================
    # BASIC RISK DEFINITION
    # =========================

    if "what is risk" in message_lower:

        return (
            "Risk means the possibility of loss or problems "
            "that may affect business performance."
        )

    if "what is overall risk" in message_lower:

        overall = prediction.get("overall_risk", None)

        if overall is not None:

            return (
                f"Your overall business risk is "
                f"{round(overall,2)}%. "
                "This reflects the total risk level of your business."
            )

        else:

            return "Overall risk data is not available."

    # =========================
    # OVERALL RISK
    # =========================

    if "overall" in message_lower:

        overall = prediction.get("overall_risk", None)

        if overall is not None:

            response = (
                f"Your overall business risk is "
                f"{round(overall,2)}%. "
                "This reflects the total risk level of your business."
            )

        else:

            response = "Overall risk data is not available."

    # =========================
    # SAFETY BLOCK — PREVENT RISK INCREASE ADVICE
    # =========================

    elif (
            "increase risk" in message_lower
            or "how to increase risk" in message_lower
            or "ways to increase risk" in message_lower
    ):

        response = (
            "Increasing risk is not recommended for business safety.\n"
            "1. High risk can lead to financial losses.\n"
            "2. It may reduce customer trust.\n"
            "3. It can cause operational failures.\n"
            "4. It increases chances of unexpected problems.\n"
            "5. Focus on reducing risk to protect your business."
        )

    # =========================
    # IMPROVEMENT / STRATEGY QUESTIONS
    # =========================

    elif any(word in message_lower for word in [

        "increase",
        "improve",
        "reduce",
        "how to",
        "strategy",
        "plan",
        "fix",
        "control",
        "manage"

    ]):

        # Pass profit ONLY if question contains 'profit'

        profit = None

        if "profit" in message_lower:
            profit = prediction.get("Profit")

        ai_reply = await generate_ai_response(
            message,
            prediction,
            graph_data,
            profit
        )

        return ai_reply

    # =========================
    # FINANCIAL RISK
    # =========================

    elif "financial" in message_lower:

        val = prediction.get("financial_risk", None)

        if val is not None:

            response = (
                f"Your financial risk is {round(val,2)}%. "
                "This risk depends on revenue, expenses, and savings."
            )

        else:

            response = "Financial risk data is not available."

    # =========================
    # OPERATIONAL RISK
    # =========================

    elif "operational" in message_lower:

        val = prediction.get("operational_risk", None)

        if val is not None:

            response = (
                f"Operational risk is {round(val,2)}%. "
                "This relates to internal business operations."
            )

        else:

            response = "Operational risk data is not available."

    # =========================
    # BEHAVIORAL RISK
    # =========================

    elif "behavioral" in message_lower:

        val = prediction.get("behavioral_risk", None)

        if val is not None:

            response = (
                f"Behavioral risk is {round(val,2)}%. "
                "This depends on customer and employee behavior."
            )

        else:

            response = "Behavioral risk data is not available."

    # =========================
    # ENVIRONMENTAL RISK
    # =========================

    elif "environmental" in message_lower:

        val = prediction.get("environmental_risk", None)

        if val is not None:

            response = (
                f"Environmental risk is {round(val,2)}%. "
                "This reflects external environmental risks."
            )

        else:

            response = "Environmental risk data is not available."

    # =========================
    # PROFIT INFORMATION
    # =========================

    elif (
            "what is my profit" in message_lower
            or "show my profit" in message_lower
            or "current profit" in message_lower
            or "profit amount" in message_lower
    ):

        profit = prediction.get("Profit", None)

        if profit is not None:

            if profit > 0:

                response = (
                    f"Your current profit is {round(profit, 2)}. "
                    "Your business is earning profit."
                )

            elif profit == 0:

                response = (
                    "Your business is currently at break-even. "
                    "There is no profit or loss."
                )

            else:

                response = (
                    f"Your current loss is {abs(round(profit, 2))}. "
                    "Your business is running at a loss."
                )

        else:

            response = "Profit data is not available."

    # =========================
    # PROFIT TREND
    # =========================

    elif (

            "is my profit increasing" in message_lower

            or "profit increasing" in message_lower

    ):

        history = prediction.get("profit_history", [])

        if len(history) >= 2:

            last = history[-1]["Profit"]
            prev = history[-2]["Profit"]

            if last > prev:

                response = (
                    "Your profit trend is increasing. "
                    "Profit has improved compared to the previous month."
                )

            elif last < prev:

                response = (
                    "Your profit trend is decreasing. "
                    "Profit reduced compared to the previous month."
                )

            else:

                response = (
                    "Your profit trend is stable. "
                    "Profit remains similar to the previous month."
                )

        else:

            response = "Not enough data to determine profit trend."

    # =========================
    # SHOW PROFIT TREND DETAILS
    # =========================

    elif (
            "show profit trend" in message_lower
            or "show trend" in message_lower
            or "profit history" in message_lower
    ):

        history = prediction.get("profit_history", [])

        if len(history) >= 2:

            lines = []

            for i, record in enumerate(history):
                month = record["month"]
                profit_val = record["Profit"]

                lines.append(
                    f"{i + 1}. {month} profit was {round(profit_val, 2)}."
                )

            last = history[-1]["Profit"]
            prev = history[-2]["Profit"]

            if last > prev:

                trend_line = (
                    f"{len(lines) + 1}. Profit increased compared to previous month."
                )

            elif last < prev:

                trend_line = (
                    f"{len(lines) + 1}. Profit decreased compared to previous month."
                )

            else:

                trend_line = (
                    f"{len(lines) + 1}. Profit remained stable."
                )

            lines.append(trend_line)

            lines.append(
                f"{len(lines) + 1}. Monitor monthly financial changes regularly."
            )

            response = (
                    "Your recent profit trend:\n"
                    + "\n".join(lines)
            )

        else:

            response = "Not enough data to display profit trend."

    # =========================
    # RISK CHANGE EXPLANATION
    # =========================

    elif (
            "why did my risk increase" in message_lower
            or "why is my risk high" in message_lower
            or "explain my risk change" in message_lower
    ):

        history = prediction.get("risk_history", [])

        if len(history) >= 2:

            last = history[-1]["overall_risk"]
            prev = history[-2]["overall_risk"]

            if last > prev:

                response = (
                    "Your risk increased due to the following reasons:\n"
                    "1. Overall risk increased compared to previous month.\n"
                    "2. Operational factors may have increased risk.\n"
                    "3. Environmental conditions may have changed.\n"
                    "4. Financial activities may have affected stability.\n"
                    "5. Monitor monthly risk values carefully."
                )

            elif last < prev:

                response = (
                    "Your risk decreased due to the following reasons:\n"
                    "1. Overall risk reduced compared to previous month.\n"
                    "2. Business operations improved.\n"
                    "3. Financial management became more stable.\n"
                    "4. Environmental factors improved.\n"
                    "5. Continue monitoring performance."
                )

            else:

                response = (
                    "Your risk remained stable compared to previous month.\n"
                    "1. Business conditions are steady.\n"
                    "2. Financial patterns are consistent.\n"
                    "3. Operational processes are stable.\n"
                    "4. Continue monitoring performance.\n"
                    "5. Maintain current strategies."
                )

        else:

            response = "Not enough data to explain risk change."

    # =========================
    # BUSINESS HEALTH SUMMARY
    # =========================

    elif (
            "business summary" in message_lower
            or "health summary" in message_lower
            or "summarize my business" in message_lower
            or "show business health" in message_lower
    ):

        overall = prediction.get("overall_risk", None)
        profit = prediction.get("Profit", None)

        profit_history = prediction.get("profit_history", [])
        risk_history = prediction.get("risk_history", [])

        if overall is not None and profit is not None:

            if profit > 0:
                profit_status = "positive"
            elif profit == 0:
                profit_status = "stable"
            else:
                profit_status = "negative"

            if len(profit_history) >= 2:

                last_profit = profit_history[-1]["Profit"]
                prev_profit = profit_history[-2]["Profit"]

                if last_profit > prev_profit:
                    profit_trend = "increasing"

                elif last_profit < prev_profit:
                    profit_trend = "decreasing"

                else:
                    profit_trend = "stable"

            else:
                profit_trend = "not available"

            if len(risk_history) >= 2:

                last_risk = risk_history[-1]["overall_risk"]
                prev_risk = risk_history[-2]["overall_risk"]

                if last_risk > prev_risk:
                    risk_trend = "increasing"

                elif last_risk < prev_risk:
                    risk_trend = "decreasing"

                else:
                    risk_trend = "stable"

            else:
                risk_trend = "not available"

            response = (
                "Your business health summary:\n"
                f"1. Overall risk is {overall}, which requires regular monitoring.\n"
                f"2. Profit is {profit_status}, showing business condition.\n"
                f"3. Profit trend is {profit_trend} over recent months.\n"
                f"4. Risk trend is {risk_trend} based on latest data.\n"
                "5. Continue reviewing monthly performance to maintain stability."
            )

        else:

            response = "Business summary data is not available."

    # =========================
    # SMART BUSINESS SUGGESTIONS
    # =========================

    elif (
            "improve my business" in message_lower
            or "business suggestions" in message_lower
            or "how to improve profit" in message_lower
            or "how to reduce risk" in message_lower
            or "give suggestions" in message_lower
    ):

        overall = prediction.get("overall_risk", None)
        profit = prediction.get("Profit", None)

        profit_history = prediction.get("profit_history", [])
        risk_history = prediction.get("risk_history", [])

        suggestions = []

        if overall is not None:

            if overall > 60:
                suggestions.append(
                    "1. Reduce operational risks to improve business stability."
                )

            elif overall > 30:
                suggestions.append(
                    "1. Monitor monthly risks to prevent sudden increases."
                )

            else:
                suggestions.append(
                    "1. Maintain current risk management practices."
                )

        if profit is not None:

            if profit > 0:
                suggestions.append(
                    "2. Continue focusing on profitable products and services."
                )

            else:
                suggestions.append(
                    "2. Reduce unnecessary expenses to improve profit."
                )

        if len(profit_history) >= 2:

            last_profit = profit_history[-1]["Profit"]
            prev_profit = profit_history[-2]["Profit"]

            if last_profit < prev_profit:

                suggestions.append(
                    "3. Review recent expenses that may have reduced profit."
                )

            else:

                suggestions.append(
                    "3. Continue strategies used in high-profit months."
                )

        if len(risk_history) >= 2:

            last_risk = risk_history[-1]["overall_risk"]
            prev_risk = risk_history[-2]["overall_risk"]

            if last_risk > prev_risk:

                suggestions.append(
                    "4. Identify factors causing increased risk."
                )

            else:

                suggestions.append(
                    "4. Maintain current risk control strategies."
                )

        suggestions.append(
            "5. Regularly review monthly performance for better planning."
        )

        response = (
                "To improve your business:\n"
                + "\n".join(suggestions)
        )

    # =========================
    # HIGHEST RISK DETECTION
    # =========================

    elif (
            "highest risk" in message_lower
            or "which risk is highest" in message_lower
            or "most risky" in message_lower
    ):

        risks = {
            "Financial Risk": prediction.get("financial_risk", 0),
            "Operational Risk": prediction.get("operational_risk", 0),
            "Environmental Risk": prediction.get("environmental_risk", 0),
            "Behavioral Risk": prediction.get("behavioral_risk", 0)
        }

        highest_risk = max(risks, key=risks.get)
        highest_value = risks[highest_risk]

        response = (
            f"{highest_risk} is currently the highest at {highest_value}.\n"
            "1. Focus on reducing this risk category first.\n"
            "2. Monitor related business activities carefully.\n"
            "3. Improve planning in this area.\n"
            "4. Review performance regularly.\n"
            "5. Maintain preventive strategies."
        )

    # =========================
    # WARNING & ALERT SYSTEM
    # =========================

    elif (
            "warning" in message_lower
            or "alert" in message_lower
            or "any risk warning" in message_lower
            or "is my business at risk" in message_lower
    ):

        warnings = []

        overall = prediction.get("overall_risk", 0)

        profit_history = prediction.get("profit_history", [])
        risk_history = prediction.get("risk_history", [])

        operational = prediction.get("operational_risk", 0)

        if overall > 60:
            warnings.append(
                "Overall risk is very high and needs attention."
            )

        if len(risk_history) >= 2:

            last_risk = risk_history[-1]["overall_risk"]
            prev_risk = risk_history[-2]["overall_risk"]

            if last_risk > prev_risk:
                warnings.append(
                    "Risk increased compared to previous month."
                )

        if len(profit_history) >= 2:

            last_profit = profit_history[-1]["Profit"]
            prev_profit = profit_history[-2]["Profit"]

            if last_profit < prev_profit:
                warnings.append(
                    "Profit decreased recently."
                )

        if operational > 60:
            warnings.append(
                "Operational risk is very high."
            )

        if not warnings:

            warnings = [
                "Business conditions are stable.",
                "Profit and risk levels are controlled.",
                "Continue monitoring monthly data.",
                "Maintain current strategies.",
                "Regular review helps maintain stability."
            ]

            numbered = "\n".join(
                [f"{i + 1}. {w}" for i, w in enumerate(warnings)]
            )

            response = (
                    "No major warnings detected:\n"
                    + numbered
            )

        else:

            warnings.append(
                "Take preventive actions to improve business stability."
            )

            numbered = "\n".join(
                [f"{i + 1}. {w}" for i, w in enumerate(warnings)]
            )

            response = (
                    "Warning detected:\n"
                    + numbered
            )

    # =========================
    # RISK RANKING SYSTEM
    # =========================

    elif (
            "risk ranking" in message_lower
            or "show risk ranking" in message_lower
            or "rank my risks" in message_lower
    ):

        risks = {

            "Financial Risk": prediction.get("financial_risk", 0),

            "Operational Risk": prediction.get("operational_risk", 0),

            "Environmental Risk": prediction.get("environmental_risk", 0),

            "Behavioral Risk": prediction.get("behavioral_risk", 0)

        }

        sorted_risks = sorted(
            risks.items(),
            key=lambda x: x[1],
            reverse=True
        )

        lines = []

        for i, (risk_name, value) in enumerate(sorted_risks):
            lines.append(
                f"{i + 1}. {risk_name} – {round(value, 2)}"
            )

        response = (
                "Risk ranking:\n"
                + "\n".join(lines)
        )

    # =========================
    # GRAPH QUESTIONS (FINAL SAFE ZONE)
    # =========================

    elif (

            "lowest" in message_lower

            and "sales" in message_lower

    ):

        if graph_data:

            lowest_month = graph_data.get("lowest_month")

            if lowest_month:

                response = (

                    f"The lowest sales month is {lowest_month}."

                )


            else:

                response = "Lowest sales data not available."


        else:

            response = "Graph data not available."

    # =========================
    # SALES TREND DIRECTION
    # =========================

    elif (
            "sales trend" in message_lower
            or "trend direction" in message_lower
            and "sales" in message_lower
    ):

        if graph_data:

            trend = graph_data.get("trend")

            if trend is not None:

                if trend > 0:

                    response = (
                        "Your sales trend is increasing "
                        "over recent months."
                    )

                else:

                    response = (
                        "Your sales trend is decreasing "
                        "over recent months."
                    )

            else:

                response = "Sales trend data not available."

        else:

            response = "Graph data not available."

    elif "trend" in message_lower:

        if graph_data:

            if graph_data["trend"] > 0:

                response = (
                    "Your overall risk trend is increasing "
                    "over recent months."
                )

            else:

                response = (
                    "Your overall risk trend is decreasing "
                    "over recent months."
                )

        else:

            response = "Trend data not available."

    # =========================
    # DEFAULT RESPONSE (AI SAFE CALL)
    # =========================

    else:

        try:

            response = await generate_ai_response(
                message,
                prediction,
                graph_data
            )

        except Exception:

            response = (
                "I'm sorry, I couldn't process that question."
            )

    # =========================
    # FINAL TONE ADJUSTMENT
    # =========================

    if friendly_mode and is_negative:

        response = "Hey bro, I understand your concern. " + response

    elif friendly_mode:

        response = "Hey bro, " + response

    elif is_negative:

        response = "I understand your concern. " + response

    elif sentiment == "positive":

        response = "Glad to assist you! " + response

    return response