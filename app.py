from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
# Replace this with the actual raw GitHub URL to your parquet file once it's
# pushed to a public repo. Pattern:
#   https://github.com/USER/REPO/blob/BRANCH/path/to/file.parquet
#   -> https://raw.githubusercontent.com/USER/REPO/BRANCH/path/to/file.parquet
POLYMARKET_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/"
    "data/processed/cluster_assignments.parquet"
)

def load_polymarket_data():
    """Load the Polymarket cluster data from GitHub.

    Returns an empty DataFrame with a placeholder column if the fetch fails,
    so the app still renders instead of crashing on startup.
    """
    try:
        return pd.read_parquet(POLYMARKET_DATA_URL)
    except Exception as e:
        print(f"Could not load Polymarket data: {e}")
        return pd.DataFrame({"note": ["data not yet available"]})

df_polymarket = load_polymarket_data()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(__name__)
server = app.server  # exposed for Docker/gunicorn if you switch off the dev server later

def project_card(title, description, link_text="View project"):
    return html.Div(
        [
            html.H3(title),
            html.P(description),
            html.A(link_text, href="#", style={"fontWeight": "bold"}),
        ],
        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "20px",
            "marginBottom": "20px",
        },
    )

def polymarket_figure():
    if "cluster" not in df_polymarket.columns:
        return px.scatter(title="Polymarket data not loaded yet")
    return px.scatter(
        df_polymarket,
        x=df_polymarket.columns[0],
        y=df_polymarket.columns[1],
        color="cluster",
        title="Polymarket Market Clusters",
    )

app.layout = html.Div(
    [
        html.H1("Data Science Portfolio"),
        html.P("A collection of data science projects with interactive visualizations."),
        html.Hr(),

        project_card(
            "Detecting Informed Trading on Polymarket",
            "Clustering analysis on ~7,600 prediction markets to flag potential "
            "informed trading patterns, validated against known cases.",
        ),
        dcc.Graph(figure=polymarket_figure()),

        html.Hr(),
        project_card(
            "Project B (coming soon)",
            "Placeholder for your next project.",
        ),
    ],
    style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "sans-serif"},
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
