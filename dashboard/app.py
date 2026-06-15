from pathlib import Path
import pandas as pd

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

# ==================================================
# LOAD DATA
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "traffic.csv"

df = pd.read_csv(DATA_PATH)

# ==================================================
# KPI METRICS
# ==================================================

records = len(df)
avg_conversion = round(df["Conversion Rate"].mean(), 2)
avg_bounce = round(df["Bounce Rate"].mean(), 2)
avg_session = round(df["Session Duration"].mean(), 2)

# ==================================================
# CHARTS
# ==================================================

traffic_conversion = (
    df.groupby("Traffic Source")["Conversion Rate"]
    .mean()
    .reset_index()
)

fig_conversion = px.bar(
    traffic_conversion,
    x="Traffic Source",
    y="Conversion Rate",
    title="Conversion Rate by Traffic Source",
    template="plotly_dark",
)

fig_conversion.update_layout(
    paper_bgcolor="#06090f",
    plot_bgcolor="#06090f",
)

fig_bounce = px.histogram(
    df,
    x="Bounce Rate",
    title="Bounce Rate Distribution",
    template="plotly_dark",
)

fig_bounce.update_layout(
    paper_bgcolor="#06090f",
    plot_bgcolor="#06090f",
)

fig_session = px.histogram(
    df,
    x="Session Duration",
    title="Session Duration Distribution",
    template="plotly_dark",
)

fig_session.update_layout(
    paper_bgcolor="#06090f",
    plot_bgcolor="#06090f",
)

corr = df.select_dtypes(include="number").corr()

fig_heatmap = px.imshow(
    corr,
    text_auto=True,
    title="Correlation Heatmap",
    template="plotly_dark",
)

fig_heatmap.update_layout(
    paper_bgcolor="#06090f",
    plot_bgcolor="#06090f",
)

# ==================================================
# APP
# ==================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG]
)

# ==================================================
# LAYOUT
# ==================================================

app.layout = dbc.Container(

    [

        # ---------------------------
        # HEADER
        # ---------------------------

        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Website Traffic Analysis Dashboard",
                        className="text-center my-4"
                    )
                )
            ]
        ),

        # ---------------------------
        # KPI CARDS
        # ---------------------------

        dbc.Row(

            [

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Total Records"),
                                html.H2(records)
                            ]
                        )
                    ),
                    xs=12,
                    sm=6,
                    lg=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Avg Conversion Rate"),
                                html.H2(avg_conversion)
                            ]
                        )
                    ),
                    xs=12,
                    sm=6,
                    lg=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Avg Bounce Rate"),
                                html.H2(avg_bounce)
                            ]
                        )
                    ),
                    xs=12,
                    sm=6,
                    lg=3
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Avg Session Duration"),
                                html.H2(avg_session)
                            ]
                        )
                    ),
                    xs=12,
                    sm=6,
                    lg=3
                ),

            ],

            className="mb-5 g-4"

        ),

        # ---------------------------
        # FIRST ROW
        # ---------------------------

        dbc.Row(

            [

                dbc.Col(
                    dcc.Graph(figure=fig_conversion),
                    xs=12,
                    lg=6
                ),

                dbc.Col(
                    dcc.Graph(figure=fig_heatmap),
                    xs=12,
                    lg=6
                ),

            ],

            className="mb-4"

        ),

        # ---------------------------
        # SECOND ROW
        # ---------------------------

        dbc.Row(

            [

                dbc.Col(
                    dcc.Graph(figure=fig_bounce),
                    xs=12,
                    lg=6
                ),

                dbc.Col(
                    dcc.Graph(figure=fig_session),
                    xs=12,
                    lg=6
                ),

            ],

            className="mb-5"

        ),

        # ---------------------------
        # RECOMMENDATIONS
        # ---------------------------

        dbc.Row(

            [

                dbc.Col(

                    dbc.Card(

                        dbc.CardBody(

                            [

                                html.H3(
                                    "Business Recommendations",
                                    className="text-center mb-4"
                                ),

                                html.Ul(
                                    [

                                        html.Li(
                                            "Focus marketing investment on the highest-converting traffic source."
                                        ),

                                        html.Li(
                                            "Reduce bounce rates by improving landing page experience."
                                        ),

                                        html.Li(
                                            "Increase engagement to improve session duration."
                                        ),

                                        html.Li(
                                            "Target returning visitors using remarketing campaigns."
                                        ),

                                    ]
                                )

                            ]

                        )

                    ),

                    lg=8,
                    className="mx-auto"

                )

            ],

            className="mb-5"

        ),

    ],

    fluid=True

)

# ==================================================
# RUN APP
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)