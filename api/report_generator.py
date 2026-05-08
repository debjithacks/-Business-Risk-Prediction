print("### NEW STYLED REPORT FILE LOADED ###")

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import Image


def generate_business_report(
    prediction,
    profit=None,
    risk_ranking=None,
    strength_score=None,
    risk_graph=None,
    profit_graph=None
):

    print(">>> NEW STYLED REPORT RUNNING <<<")

    file_path = f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    styles = getSampleStyleSheet()

    elements = []

    # =========================
    # PROJECT HEADER
    # =========================

    elements.append(
        Paragraph(
            "<font size=14><b>Business Risk Prediction System</b></font>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 4))

    elements.append(
        Paragraph(
            "<font size=12>Final Year Project Report</font>",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 10))

    # MAIN TITLE

    elements.append(
        Paragraph(
            "<font size=18><b>Business Risk & Performance Report</b></font>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 6))

    # SEPARATOR LINE

    line_table = Table(
        [[""]],
        colWidths=[480]
    )

    line_table.setStyle(
        TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 2, colors.black)
        ])
    )

    elements.append(line_table)

    elements.append(Spacer(1, 12))


    elements.append(
        Paragraph(
            f"<b>Generated On:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # =========================
    # RISK SUMMARY
    # =========================

    elements.append(
        Paragraph("<b>Risk Summary</b>", styles["Heading2"])
    )

    risk_data = [

        ["Risk Type", "Value"],

        ["Overall Risk", prediction.get("overall_risk")],

        ["Financial Risk", prediction.get("financial_risk")],

        ["Operational Risk", prediction.get("operational_risk")],

        ["Environmental Risk", prediction.get("environmental_risk")],

        ["Behavioral Risk", prediction.get("behavioral_risk")]

    ]

    risk_table = Table(risk_data, colWidths=[220, 120])

    risk_table.setStyle(

        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)

        ])

    )

    elements.append(Spacer(1, 10))
    elements.append(risk_table)

    elements.append(Spacer(1, 20))

    # =========================
    # PROFIT SUMMARY
    # =========================

    if profit is not None:

        elements.append(
            Paragraph("<b>Profit Summary</b>", styles["Heading2"])
        )

        profit_table = Table(

            [

                ["Metric", "Value"],

                ["Latest Profit", profit]

            ],

            colWidths=[220, 120]

        )

        profit_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)

            ])

        )

        elements.append(Spacer(1, 10))
        elements.append(profit_table)

        elements.append(Spacer(1, 20))

    # =========================
    # RISK RANKING
    # =========================

    if risk_ranking:

        elements.append(
            Paragraph("<b>Risk Ranking</b>", styles["Heading2"])
        )

        ranking_data = [["Rank", "Risk Type", "Value"]]

        count = 1

        for risk_name, value in risk_ranking:

            ranking_data.append(
                [count, risk_name, value]
            )

            count += 1

        ranking_table = Table(

            ranking_data,

            colWidths=[60, 160, 120]

        )

        ranking_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)

            ])

        )

        elements.append(Spacer(1, 10))
        elements.append(ranking_table)

        elements.append(Spacer(1, 20))

    # =========================
    # STRENGTH SCORE
    # =========================

    if strength_score is not None:

        elements.append(
            Paragraph("<b>Business Strength Score</b>", styles["Heading2"])
        )

        strength_table = Table(

            [

                ["Metric", "Score"],

                ["Strength Score", f"{strength_score} / 100"]

            ],

            colWidths=[220, 120]

        )

        strength_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.orange),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)

            ])

        )

        elements.append(Spacer(1, 10))
        elements.append(strength_table)

    # =========================
    # GRAPH SECTION
    # =========================

    if risk_graph:
        elements.append(
            Paragraph(
                "<b>Risk Trend Graph</b>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        elements.append(
            Image(
                risk_graph,
                width=400,
                height=200
            )
        )

        elements.append(Spacer(1, 20))

    if profit_graph:
        elements.append(
            Paragraph(
                "<b>Profit Trend Graph</b>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        elements.append(
            Image(
                profit_graph,
                width=400,
                height=200
            )
        )

        elements.append(Spacer(1, 20))
    # =========================
    # FOOTER
    # =========================

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "<font size=9 color=grey>"
            "Generated by Business Risk Prediction System"
            "</font>",
            styles["Normal"]
        )
    )

    # =========================
    # BUILD PDF
    # =========================

    # =========================
    # FOOTER FUNCTION
    # =========================

    def add_page_footer(canvas, doc):

        canvas.saveState()

        # ONLY add page number (keep existing footer unchanged)

        page_number_text = f"Page {doc.page}"

        canvas.drawRightString(
            550,
            20,
            page_number_text
        )

        canvas.restoreState()

    # =========================
    # BUILD PDF WITH FOOTER
    # =========================

    doc = SimpleDocTemplate(

        file_path,

        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=50

    )

    doc.build(

        elements,

        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer

    )

    return file_path