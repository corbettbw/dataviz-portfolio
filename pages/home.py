import dash
from dash import html

dash.register_page(__name__, path="/", name="Home")

CARD_STYLE = {
    "border": "1px solid #e9ecef",
    "borderRadius": "8px",
    "padding": "24px",
    "backgroundColor": "#fff",
    "display": "flex",
    "flexDirection": "column",
    "gap": "8px",
    "textDecoration": "none",
    "color": "inherit",
    "transition": "box-shadow 0.15s",
}

TAG_STYLE = {
    "display": "inline-block",
    "fontSize": "11px",
    "fontWeight": "600",
    "padding": "2px 8px",
    "borderRadius": "4px",
    "marginRight": "4px",
}

def tag(label, color):
    return html.Span(label, style={**TAG_STYLE, "backgroundColor": color, "color": "#fff"})

PROJECTS = [
    {
        "title": "Informed Trading Detection",
        "href": "/polymarket",
        "description": (
            "Unsupervised ML pipeline to surface anomalous activity on Polymarket "
            "prediction markets. K-means clustering and Isolation Forest applied to "
            "six behavioral features across 476 markets."
        ),
        "tags": [("K-Means", "#3498db"), ("Isolation Forest", "#9b59b6"), ("Polymarket", "#e67e22")],
        "stat": "476 markets analyzed",
    },
    {
        "title": "Marine Mammal Conservation",
        "href": "/iucn",
        "description": (
            "Interactive explorer for IUCN Red List assessments of 187 marine mammal "
            "species. Select a species to see its geographic range and Wikipedia summary."
        ),
        "tags": [("IUCN", "#2ecc71"), ("Choropleth", "#1abc9c"), ("Conservation", "#27ae60")],
        "stat": "187 species · 17,000+ range records",
    },
    {
        "title": "Hospital Readmission Risk",
        "href": "/hospital",
        "description": (
            "Binary classification model predicting 30-day hospital readmissions "
            "on the UCI Diabetes dataset (~100k records, 50 features). "
            "Logistic Regression and Random Forest with AUC ~0.64."
        ),
        "tags": [("Random Forest", "#e74c3c"), ("Logistic Regression", "#c0392b"), ("UCI", "#7f8c8d")],
        "stat": "100k records · AUC 0.64",
    },
]

layout = html.Div(
    style={"fontFamily": "system-ui, sans-serif", "color": "#212529", "backgroundColor": "#f8f9fa", "minHeight": "100vh"},
    children=[
        html.Div(
            style={"maxWidth": "960px", "margin": "0 auto", "padding": "80px 24px 40px"},
            children=[
                html.H1("Corbett Winningham", style={"fontSize": "2.2rem", "fontWeight": "700", "marginBottom": "8px"}),
                html.P(
                    "Data scientist and software engineer. These projects explore machine learning, "
                    "behavioral analysis, and conservation data.",
                    style={"color": "#6c757d", "fontSize": "1.1rem", "marginBottom": "48px"},
                ),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "24px"},
                    children=[
                        html.A(
                            href=p["href"],
                            style=CARD_STYLE,
                            children=[
                                html.Div(
                                    [tag(label, color) for label, color in p["tags"]],
                                    style={"marginBottom": "4px"},
                                ),
                                html.H2(p["title"], style={"fontSize": "1.1rem", "fontWeight": "600", "margin": "0"}),
                                html.P(p["description"], style={"color": "#495057", "fontSize": "14px", "lineHeight": "1.6", "margin": "0", "flexGrow": "1"}),
                                html.Div(p["stat"], style={"fontSize": "12px", "color": "#adb5bd", "marginTop": "8px"}),
                            ],
                        )
                        for p in PROJECTS
                    ],
                ),
            ],
        ),
    ],
)