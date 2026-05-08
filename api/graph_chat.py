# graph_chat.py

from prediction import generate_risk_history


async def analyze_user_graph(user_id):

    history = await generate_risk_history(user_id)

    if not history:
        return None

    months = history["months"]
    overall = history["overall"]

    if not months or not overall:
        return None

    # Highest Risk
    highest_value = max(overall)
    highest_index = overall.index(highest_value)

    highest_month = months[highest_index]

    # Lowest Risk
    lowest_value = min(overall)
    lowest_index = overall.index(lowest_value)

    lowest_month = months[lowest_index]

    # Trend
    trend = 0

    if len(overall) > 1:
        trend = overall[-1] - overall[0]

    return {
        "highest_month": highest_month,
        "highest_value": highest_value,
        "lowest_month": lowest_month,
        "lowest_value": lowest_value,
        "trend": trend
    }

# =========================
# MONTH COMPARISON FUNCTION
# =========================

async def compare_two_months(user_id, month1, month2):

    history = await generate_risk_history(user_id)

    if not history:
        return None

    months = history["months"]
    overall = history["overall"]

    if month1 not in months or month2 not in months:
        return None

    idx1 = months.index(month1)
    idx2 = months.index(month2)

    risk1 = overall[idx1]
    risk2 = overall[idx2]

    return {
        "month1": month1,
        "month2": month2,
        "risk1": risk1,
        "risk2": risk2
    }