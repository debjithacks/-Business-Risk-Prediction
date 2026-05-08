import joblib
import pandas as pd
import numpy as np
import os

from database import risk_data_collection, user_collection


# =========================================
# SAFE MODEL PATH SETUP
# =========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "..",
    "models"
)


# =========================================
# LOAD MODELS
# =========================================

overall_model = joblib.load(
    os.path.join(MODEL_DIR, "overall_model.pkl")
)

scaler = joblib.load(
    os.path.join(MODEL_DIR, "scaler.pkl")
)

model_columns = joblib.load(
    os.path.join(MODEL_DIR, "model_columns.pkl")
)

fin_model = joblib.load(
    os.path.join(MODEL_DIR, "financial_model.pkl")
)

op_model = joblib.load(
    os.path.join(MODEL_DIR, "operational_model.pkl")
)

env_model = joblib.load(
    os.path.join(MODEL_DIR, "environmental_model.pkl")
)

beh_model = joblib.load(
    os.path.join(MODEL_DIR, "behavioral_model.pkl")
)

individual_columns = joblib.load(
    os.path.join(
        MODEL_DIR,
        "individual_model_columns.pkl"
    )
)

financial_cols = individual_columns["financial"]
operational_cols = individual_columns["operational"]
environmental_cols = individual_columns["environmental"]
behavioral_cols = individual_columns["behavioral"]


# =========================================
# UTILITY FUNCTIONS
# =========================================

async def get_user_business_type(user_id):

    user = await user_collection.find_one(
        {"username": user_id}
    )

    if user:

        return user.get(
            "business_type",
            "General"
        )

    return "General"



def get_monthly_rainfall(month):

    rainfall_map = {

        "Jan": 5,
        "Feb": 10,
        "Mar": 15,
        "Apr": 30,
        "May": 120,
        "Jun": 300,
        "Jul": 350,
        "Aug": 320,
        "Sep": 250,
        "Oct": 100,
        "Nov": 30,
        "Dec": 10

    }

    return rainfall_map.get(
        month[:3],
        0
    )


# =========================================
# STORE USER DATA (FIXED)
# =========================================

async def store_user_month_data(
    user_id,
    month,
    month_data
):

    # Default fallback values

    defaults = {

        "Total_Sales": 0,
        "Total_Expenses": 0,
        "Profit": 0,
        "Maintenance_Cost": 0,
        "Machine_Usage_Hours": 0,
        "Breakdown_Count": 0,
        "Holiday_Count": 0,
        "Sentiment_Score": 0

    }

    # Fill missing keys

    for key in defaults:

        if key not in month_data:

            month_data[key] = defaults[key]


    month_data["user_id"] = user_id

    month_data["month"] = month

    month_data["Rainfall"] = get_monthly_rainfall(
        month
    )


    await risk_data_collection.update_one(

        {

            "user_id": user_id,
            "month": month

        },

        {

            "$set": month_data

        },

        upsert=True

    )


# =========================================
# MAIN PREDICTION FUNCTION
# =========================================

async def cumulative_prediction(user_id):

    cursor = risk_data_collection.find(
        {"user_id": user_id}
    )

    user_months = await cursor.to_list(
        length=100
    )

    if not user_months:

        return {}


    df = pd.DataFrame(user_months)

    latest_month = df["month"].iloc[-1]


    # ===============================
    # PREPARE MODEL INPUT
    # ===============================

    full_df = pd.DataFrame(

        0,

        index=range(len(df)),

        columns=model_columns

    )


    for col in df.columns:

        if col in model_columns:

            full_df[col] = df[col]


    rain_val = df.get(
        "Rainfall",
        pd.Series([0])
    ).iloc[-1]


    for r_col in [

        "Rainfall_mm",
        "Monthly_Rainfall_Avg",
        "Rainfall_Deviation"

    ]:

        if r_col in model_columns:

            full_df[r_col] = rain_val


    # Business type

    bus_type = await get_user_business_type(
        user_id
    )

    bus_col = f"Business_Type_{bus_type}"

    if bus_col in model_columns:

        full_df[bus_col] = 1


    # Season logic

    month_prefix = latest_month[:3]

    if (

        month_prefix in
        ["Jun", "Jul", "Aug", "Sep"]

        and
        "Season_Monsoon" in model_columns

    ):

        full_df["Season_Monsoon"] = 1


    elif (

        month_prefix in
        ["Mar", "Apr", "May"]

        and
        "Season_Summer" in model_columns

    ):

        full_df["Season_Summer"] = 1


    elif "Season_Winter" in model_columns:

        full_df["Season_Winter"] = 1


    if "Sales_Trend_0.0" in model_columns:

        full_df["Sales_Trend_0.0"] = 1


    latest_row = full_df.iloc[[-1]]

    latest_row = latest_row.apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0)


    # ===============================
    # SAFE PREDICTIONS
    # ===============================

    overall_risk = float(

        np.nan_to_num(

            overall_model.predict(

                scaler.transform(latest_row)

            )[0]

        )

    )


    financial_risk = float(

        np.nan_to_num(

            fin_model.predict(

                latest_row[financial_cols]

            )[0]

        )

    )


    operational_risk = float(

        np.nan_to_num(

            op_model.predict(

                latest_row[operational_cols]

            )[0]

        )

    )


    environmental_risk = float(

        np.nan_to_num(

            env_model.predict(

                latest_row[environmental_cols]

            )[0]

        )

    )


    behavioral_risk = float(

        np.nan_to_num(

            beh_model.predict(

                latest_row[behavioral_cols]

            )[0]

        )

    )


    # ===============================
    # SAFE OUTPUT
    # ===============================

    risk_results = {

        "financial_risk":
            round(financial_risk, 2),

        "operational_risk":
            round(operational_risk, 2),

        "environmental_risk":
            round(environmental_risk, 2),

        "behavioral_risk":
            round(behavioral_risk, 2),

        "overall_risk":
            round(overall_risk, 2),

        "Profit":
            float(np.nan_to_num(
                df.get("Profit",
                       pd.Series([0])).iloc[-1]
            )),

        "Total_Sales":
            float(np.nan_to_num(
                df.get("Total_Sales",
                       pd.Series([0])).iloc[-1]
            )),

        "Total_Expenses":
            float(np.nan_to_num(
                df.get("Total_Expenses",
                       pd.Series([0])).iloc[-1]
            )),

        "Maintenance_Cost":
            float(np.nan_to_num(
                df.get("Maintenance_Cost",
                       pd.Series([0])).iloc[-1]
            ))

    }


    # ===============================
    # SAVE RESULTS
    # ===============================

    await risk_data_collection.update_one(

        {

            "user_id": user_id,
            "month": latest_month

        },

        {

            "$set": risk_results

        }

    )


    # ===============================
    # SAFE HISTORY FIX
    # ===============================

    recent_months = df.tail(6).fillna(0)


    profit_history = []

    for _, row in recent_months.iterrows():

        profit_history.append({

            "month":
                row.get("month", ""),

            "Profit":
                float(np.nan_to_num(
                    row.get("Profit", 0)
                ))

        })

    risk_history = []

    for _, row in recent_months.iterrows():

        month_name = row.get("month", "")

        risk_val = float(
            np.nan_to_num(
                row.get("overall_risk", 0)
            )
        )

        # Fix latest month zero issue
        if risk_val == 0 and month_name == latest_month:
            risk_val = overall_risk

        risk_history.append({

            "month": month_name,

            "overall_risk": risk_val

        })


    risk_results["profit_history"] = profit_history

    risk_results["risk_history"] = risk_history

    # ===============================
    # GENERATE BUSINESS DNA (NEW)
    # ===============================

    dna_profile = generate_business_dna(

        financial_risk,
        operational_risk,
        environmental_risk,
        behavioral_risk,
        profit_history,
        risk_history

    )
    risk_results["dna_profile"] = dna_profile

    # ===============================
    # GENERATE COMPLETE DNA HISTORY
    # ===============================

    dna_history = []

    for month_data in risk_history:

        month_risk = month_data["overall_risk"]

        # If risk is zero, replace with latest calculated risk
        if month_risk == 0:
            month_risk = overall_risk

        dna_strength = round(
            100 - month_risk,
            2
        )

        dna_history.append({

            "month": month_data["month"],

            "dna_strength": dna_strength

        })

    risk_results["dna_history"] = dna_history

    # ===============================
    # DETECT DNA MUTATIONS
    # ===============================

    mutation_alerts = detect_dna_mutation(
        dna_history
    )

    risk_results["dna_mutations"] = mutation_alerts

    dna_type = classify_dna(dna_profile)

    risk_results["dna_type"] = dna_type

    # ===============================
    # GENERATE RISK FORECAST
    # ===============================

    forecast_data = forecast_future_risk(
        risk_history
    )

    risk_results["risk_forecast"] = forecast_data

    return risk_results

# =========================================
# GENERATE HISTORY GRAPH
# =========================================

async def generate_risk_history(user_id):

    cursor = risk_data_collection.find(
        {"user_id": user_id}
    )

    docs = await cursor.to_list(
        length=100
    )


    history = {

        "months": [],
        "overall": [],
        "financial": [],
        "operational": [],
        "environmental": [],
        "behavioral": []

    }


    for d in docs:

        history["months"].append(
            d.get("month")
        )

        for key in [

            "overall",
            "financial",
            "operational",
            "environmental",
            "behavioral"

        ]:

            history[key].append(

                float(

                    np.nan_to_num(

                        d.get(
                            f"{key}_risk",
                            0
                        )

                    )

                )

            )


    return history

# =========================================
# BUSINESS DNA GENERATION (NEW FEATURE)
# =========================================

def generate_business_dna(
        financial_risk,
        operational_risk,
        environmental_risk,
        behavioral_risk,
        profit_history,
        risk_history
):

    # -------------------------------------
    # 1️⃣ Financial Stability Index
    # -------------------------------------

    financial_stability = max(
        0,
        100 - financial_risk
    )

    # -------------------------------------
    # 2️⃣ Operational Efficiency Index
    # -------------------------------------

    operational_efficiency = max(
        0,
        100 - operational_risk
    )

    # -------------------------------------
    # 3️⃣ Environmental Sensitivity Index
    # -------------------------------------

    environmental_sensitivity = environmental_risk

    # -------------------------------------
    # 4️⃣ Behavioral Trust Index
    # -------------------------------------

    behavioral_trust = max(
        0,
        100 - behavioral_risk
    )

    # -------------------------------------
    # 5️⃣ Business Adaptability Index
    # (Uses trend stability — Novel part)
    # -------------------------------------

    adaptability = 50  # default value

    try:

        if len(risk_history) >= 2:

            last_risk = risk_history[-1][
                "overall_risk"
            ]

            prev_risk = risk_history[-2][
                "overall_risk"
            ]

            risk_change = abs(
                last_risk - prev_risk
            )

            adaptability = max(
                0,
                100 - risk_change
            )

    except Exception:

        adaptability = 50

    # -------------------------------------
    # FINAL DNA VECTOR
    # -------------------------------------

    dna_profile = [

        round(financial_stability, 2),

        round(operational_efficiency, 2),

        round(environmental_sensitivity, 2),

        round(behavioral_trust, 2),

        round(adaptability, 2)

    ]

    return dna_profile

# ===============================
# DNA CLASSIFICATION SYSTEM
# ===============================

def classify_dna(dna):

    financial, operational, environmental, behavioral, adaptability = dna

    # High behavior-driven business
    if behavioral > 70 and financial > 50:
        return "Behavior-Driven Stable Business"

    # Strong operational focus
    elif operational > 70:
        return "Operationally Optimized Business"

    # Highly adaptive
    elif adaptability > 70:
        return "Adaptive Growth-Oriented Business"

    # Environment-sensitive
    elif environmental > 70:
        return "Environment-Sensitive Business"

    # Financial strength
    elif financial > 70:
        return "Financially Dominant Business"

    # Default
    else:
        return "Balanced Moderate-Risk Business"

# ===============================
# DNA MUTATION DETECTION
# (LATEST MONTH ONLY)
# ===============================

def detect_dna_mutation(dna_history):

    mutation_messages = []

    if len(dna_history) < 2:
        return mutation_messages

    # Get last two months only
    prev = dna_history[-2]
    curr = dna_history[-1]

    prev_strength = prev["dna_strength"]
    curr_strength = curr["dna_strength"]

    curr_month = curr["month"]

    change = curr_strength - prev_strength

    # Mutation threshold
    if abs(change) >= 10:

        if change > 0:

            message = (
                f"⚠ DNA Mutation: "
                f"Significant improvement "
                f"detected in {curr_month}."
            )

        else:

            message = (
                f"⚠ DNA Mutation: "
                f"Performance drop "
                f"detected in {curr_month}."
            )

        mutation_messages.append(message)

    return mutation_messages

# ===============================
# BUSINESS RISK FORECASTING
# ===============================

from sklearn.linear_model import LinearRegression
import numpy as np

def forecast_future_risk(risk_history):

    forecast_results = []

    if len(risk_history) < 2:
        return forecast_results

    # Prepare training data
    months = list(range(len(risk_history)))

    risks = [
        item["overall_risk"]
        for item in risk_history
        if item["overall_risk"] != 0
    ]

    if len(risks) < 2:
        return forecast_results

    X = np.array(months[:len(risks)]).reshape(-1,1)
    y = np.array(risks)

    model = LinearRegression()

    model.fit(X, y)

    # Predict next 3 months
    future_months = [

        len(risks),
        len(risks)+1,
        len(risks)+2

    ]

    predictions = model.predict(
        np.array(future_months).reshape(-1,1)
    )

    for i, value in enumerate(predictions):
        # Increasing uncertainty
        confidence = 5 + (i * 2)

        forecast_results.append({

            "month": f"Future_{i + 1}",

            "predicted_risk":
                round(float(value), 2),

            "upper_bound":
                round(float(value + confidence), 2),

            "lower_bound":
                round(float(value - confidence), 2)

        })

    # ===============================
    # FORECAST TREND ANALYSIS
    # ===============================

    if len(predictions) >= 2:

        first = predictions[0]
        last = predictions[-1]

        change = last - first

        if change > 5:

            trend_message = (
                "⚠ Forecast Insight: "
                "Risk trend shows increasing pattern. "
                "Preventive actions recommended."
            )

        elif change < -5:

            trend_message = (
                "✅ Forecast Insight: "
                "Risk trend improving steadily."
            )

        else:

            trend_message = (
                "ℹ Forecast Insight: "
                "Risk trend appears stable."
            )

        forecast_results.append({

            "trend_message": trend_message

        })

    return forecast_results