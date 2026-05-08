import matplotlib.pyplot as plt


def generate_risk_profit_graphs(data):

    months = []
    risks = []
    profits = []

    for row in data:

        months.append(row.get("month"))

        risks.append(
            row.get("overall_risk", 0)
        )

        profits.append(
            row.get("Profit", 0)
        )

    # ======================
    # RISK GRAPH
    # ======================

    plt.figure()

    plt.plot(
        months,
        risks,
        marker="o"
    )

    plt.title("Risk Trend Over Months")

    plt.xlabel("Months")

    plt.ylabel("Overall Risk")

    plt.xticks(rotation=45)

    risk_path = "risk_graph.png"

    plt.tight_layout()

    plt.savefig(risk_path)

    plt.close()

    # ======================
    # PROFIT GRAPH
    # ======================

    plt.figure()

    plt.plot(
        months,
        profits,
        marker="o"
    )

    plt.title("Profit Trend Over Months")

    plt.xlabel("Months")

    plt.ylabel("Profit")

    plt.xticks(rotation=45)

    profit_path = "profit_graph.png"

    plt.tight_layout()

    plt.savefig(profit_path)

    plt.close()

    return risk_path, profit_path