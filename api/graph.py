import plotly.graph_objs as go

def generate_graph(data):

    months = data["months"]

    fig = go.Figure()

    # Overall Risk
    fig.add_trace(
        go.Scatter(
            x=months,
            y=data["overall"],
            mode='lines+markers',
            name='Overall Risk',
            line=dict(color='black', width=4, dash='dash'), # Bold, Black, and Dotted
            marker=dict(size=8)
        )
    )

    # Financial
    fig.add_trace(
        go.Scatter(
            x=months,
            y=data["financial"],
            mode='lines+markers',
            name='Financial Risk'
        )
    )

    # Operational
    fig.add_trace(
        go.Scatter(
            x=months,
            y=data["operational"],
            mode='lines+markers',
            name='Operational Risk'
        )
    )

    # Environmental
    fig.add_trace(
        go.Scatter(
            x=months,
            y=data["environmental"],
            mode='lines+markers',
            name='Environmental Risk'
        )
    )

    # Behavioral
    fig.add_trace(
        go.Scatter(
            x=months,
            y=data["behavioral"],
            mode='lines+markers',
            name='Behavioral Risk'
        )
    )

    fig.update_layout(
        title="Business Risk Analysis",
        xaxis_title="Months",
        yaxis_title="Risk Score"
    )

    return fig.to_dict()