from dash import Dash, html, dcc, dash_table, Input, Output
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme, Symbol, Group


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
POLYMARKET_DATA_URL = (
    "https://raw.githubusercontent.com/corbettbw/prediction-market-insider/"
    "main/data/processed/cluster_assignments.parquet"
)

def load_data():
    try:
        return pd.read_parquet(POLYMARKET_DATA_URL)
    except Exception as e:
        print(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------------------------
# Feature engineering for visualization
# ---------------------------------------------------------------------------
features = ["uncertainty", "log_trading_intensity", "log_avg_trade_size",
            "late_capital_ratio", "top3_wallet_concentration", "velocity_ratio"]

feature_labels = {
    "uncertainty": "Uncertainty at Open",
    "log_trading_intensity": "Trading Intensity",
    "log_avg_trade_size": "Avg Trade Size",
    "late_capital_ratio": "Late Capital Ratio",
    "top3_wallet_concentration": "Wallet Concentration",
    "velocity_ratio": "Velocity Ratio",
}

# For display purposes — raw values instead of log-transformed
raw_display_features = ["uncertainty", "trading_intensity", "avg_trade_size",
                        "late_capital_ratio", "top3_wallet_concentration", "velocity_ratio"]

raw_feature_labels = {
    "uncertainty":               "Uncertainty at Open",
    "trading_intensity":         "Trading Intensity ($/hr)",
    "avg_trade_size":            "Avg Trade Size ($)",
    "late_capital_ratio":        "Late Capital Ratio",
    "top3_wallet_concentration": "Wallet Concentration",
    "velocity_ratio":            "Velocity Ratio",
}

known_ids = {
    "d4vd (#1 search)":         "0xea17b1284d10617a57f910b2ea63bdef481b1724a4b899d454ff104bea67b657",
    "d4vd (top 5)":             "0xeaf59fcbf65e45abac0383dad483239d849e6d48d9eb2a6b3bf5cc1c7e9cf2ad",
    "Maduro out Jan 31":        "0x580adc1327de9bf7c179ef5aaffa3377bb5cb252b7d6390b027172d43fd6f993",
    "US forces Venezuela":      "0xbb8bfdef9052b2709557a6f8f28b23551e3134bfb86eca800211e2191703ee65",
    "Israel action before July":"0xd25ff3223a2233f6cd96a349455ca3237931c64358792f90c5f02d8cc39be38d",
    "Israel strike June 24":    "0xd2055601def8961bea2e6fc911538c64ee181e7ae944f67c78f395e39df43580",
    "Israel strikes Jan 31":    "0x23fd2b26c4e095465ba0d2ebce8d5eda57009ddc59aad8b68ab19ca968b41eed",
    "George Santos SOTU":       "0x1b229b087ce4a8063eb8b183ebff486e7eabe6dad3033320dff2e0c5963c94d5",
}

if not df.empty and all(f in df.columns for f in features):
    # PCA
    X_scaled = StandardScaler().fit_transform(df[features])
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df["pc1"] = X_pca[:, 0]
    df["pc2"] = X_pca[:, 1]

    # Isolation Forest
    if "anomaly_flag" not in df.columns:
        cluster1_idx = df[df["cluster"] == 1].index
        iso = IsolationForest(contamination=0.05, random_state=42)
        X_c1 = X_scaled[df.index.get_indexer(cluster1_idx)]
        iso.fit(X_c1)
        df.loc[cluster1_idx, "anomaly_flag"] = iso.predict(X_c1)
        df.loc[cluster1_idx, "anomaly_score"] = iso.decision_function(X_c1)
    if "anomaly_raw" in df.columns and "anomaly_score" not in df.columns:
        df = df.rename(columns={"anomaly_raw": "anomaly_score"})
    df["anomaly_score"] = df.get("anomaly_score", pd.Series(0, index=df.index)).fillna(0)

    # Known cases
    df["known"] = df["market_id"].isin(known_ids.values())

    # Marker type for scatter
    df["marker_size"] = 6
    df.loc[df["anomaly_flag"] == -1, "marker_size"] = 12
    df.loc[df["known"], "marker_size"] = 16
    df["marker_type"] = "Normal"
    df.loc[df["cluster"] == 1, "marker_type"] = "High Attractiveness"
    df.loc[(df["cluster"] == 1) & (df["anomaly_flag"] == -1), "marker_type"] = "Flagged Anomaly"
    df.loc[df["known"] & (df["anomaly_flag"] != -1), "marker_type"] = "Known (not flagged)"
    df.loc[df["known"] & (df["anomaly_flag"] == -1), "marker_type"] = "Known + Flagged"

    # Cluster means for bar chart
    cluster_means = df.groupby("cluster")[features].mean().reset_index()
    cluster_means["cluster_label"] = cluster_means["cluster"].map(
        {0: "Cluster 0 — Low", 1: "Cluster 1 — High"}
    )

    # Summary numbers
    n_markets = len(df)
    n_anomalies = int((df["anomaly_flag"] == -1).sum())
    n_known_flagged = int(df[df["known"] & (df["anomaly_flag"] == -1)].shape[0])
    n_known_total = int(df["known"].sum())

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def make_scatter():
    color_map = {
        "Normal":             "#aec6cf",
        "High Attractiveness":"#e74c3c",
        "Flagged Anomaly":    "#e67e22",
        "Known (not flagged)":"#2ecc71",
        "Known + Flagged":    "gold",
    }
    fig = px.scatter(
        df, x="pc1", y="pc2",
        color="marker_type",
        size="marker_size",
        size_max=16,
        color_discrete_map=color_map,
        hover_data={
            "marker_size": False,
            "category": False,
            "volume": False,
            "marker_type": False,
            "pc1": False,
            "pc2": False,
        },
        hover_name="question",
        labels={
            "pc1": f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)",
            "pc2": f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)",
            "marker_type": "",
        },
        opacity=0.6,
        height=500,
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    fig.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    return fig


def make_feature_bars():
    rows = []
    for f in features:
        for _, row in cluster_means.iterrows():
            rows.append({
                "feature": feature_labels[f],
                "cluster": row["cluster_label"],
                "value": row[f],
            })
    bar_df = pd.DataFrame(rows)
    fig = px.bar(
        bar_df, x="value", y="feature",
        color="cluster",
        barmode="group",
        orientation="h",
        color_discrete_map={"Cluster 0 — Low": "#aec6cf", "Cluster 1 — High": "#e74c3c"},
        labels={"value": "Mean Value (log-scaled where noted)", "feature": "", "cluster": ""},
        height=350,
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    return fig

def make_importance_bars():
    importance_data = [
        {"feature": "Velocity Ratio",         "importance": 0.006,  "std": 0.001, "group": "secondary"},
        {"feature": "Uncertainty at Open",     "importance": 0.030,  "std": 0.002, "group": "secondary"},
        {"feature": "Late Capital Ratio",      "importance": 0.032,  "std": 0.003, "group": "secondary"},
        {"feature": "Avg Trade Size",          "importance": 0.093,  "std": 0.004, "group": "leading"},
        {"feature": "Trading Intensity",       "importance": 0.139,  "std": 0.006, "group": "leading"},
        {"feature": "Wallet Concentration",    "importance": 0.172,  "std": 0.005, "group": "leading"},
    ]
    imp_df = pd.DataFrame(importance_data)
    fig = px.bar(
        imp_df, x="importance", y="feature",
        orientation="h",
        error_x="std",
        color="group",
        color_discrete_map={"leading": "#e74c3c", "secondary": "#aec6cf"},
        labels={"importance": "Mean accuracy drop when feature is shuffled", "feature": "", "group": ""},
        height=300,
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=20, b=20),
        showlegend=False,
    )
    return fig

def make_anomaly_table_data():
    out = df.copy()
    out = out.sort_values(["cluster", "anomaly_score"], ascending=[False, True])
    out["known"] = out["known"].apply(lambda x: "✓" if x else "")
    return out[[
        "question", "category", "volume", "uncertainty", "trading_intensity", "avg_trade_size",
        "late_capital_ratio", "top3_wallet_concentration", "velocity_ratio", "anomaly_score", "known"
    ]].to_dict("records")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
SECTION = {
    "maxWidth": "960px",
    "margin": "0 auto",
    "padding": "60px 24px",
}

HERO_STAT = {
    "textAlign": "center",
    "padding": "24px",
    "backgroundColor": "#f8f9fa",
    "borderRadius": "8px",
    "flex": "1",
    "margin": "0 8px",
}

DIVIDER = {"borderTop": "1px solid #e9ecef", "margin": "0"}

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[])
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .js-plotly-plot .plotly .cursor-crosshair { cursor: pointer !important; }
        </style>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

server = app.server

app.layout = html.Div(style={"fontFamily": "system-ui, sans-serif", "color": "#212529"}, children=[

    # ── Hero ────────────────────────────────────────────────────────────────
    html.Div(style={**SECTION, "paddingTop": "80px"}, children=[
        html.H1("Detecting Informed Trading on Polymarket",
                style={"fontSize": "2.2rem", "fontWeight": "700", "marginBottom": "16px"}),
        html.P(
            "Prediction markets are vulnerable to traders with private information. "
            "This project uses unsupervised machine learning — K-means clustering and "
            "Isolation Forest anomaly detection — to identify markets that show structural "
            "signatures of informed trading, without being told which markets were actually targeted.",
            style={"fontSize": "1.1rem", "color": "#495057", "maxWidth": "720px",
                   "lineHeight": "1.7", "marginBottom": "40px"},
        ),
        html.Div(style={"display": "flex"}, children=[
            html.Div(style=HERO_STAT, children=[
                html.Div(f"{n_markets:,}", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                html.Div("markets analyzed", style={"color": "#6c757d"}),
            ]),
            html.Div(style=HERO_STAT, children=[
                html.Div(f"{n_anomalies}", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                html.Div("anomalies flagged", style={"color": "#6c757d"}),
            ]),
            html.Div(style=HERO_STAT, children=[
                html.Div(f"{n_known_flagged}/{n_known_total}", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                html.Div("known cases correctly identified", style={"color": "#6c757d"}),
            ]),
        ]),
    ]),

    html.Hr(style=DIVIDER),

    # ── Section 1: Clustering ───────────────────────────────────────────────
    html.Div(style=SECTION, children=[
        html.H2("The Clustering", style={"marginBottom": "8px"}),
        html.P(
            "Each dot is a market. K-means clustering separated 2,310 markets into two groups "
            "based on six behavioral features. Red markets scored high on informed trading "
            "attractiveness. Known insider trading cases are highlighted.",
            style={"color": "#495057", "marginBottom": "24px"},
        ),
        html.Div(
            dcc.Graph(id="pca-scatter", figure=make_scatter()),
            style={"cursor": "pointer"}
        ),

        # Market detail directly below scatter
        html.Div(style={"marginTop": "24px"}, children=[
            html.H5("Market Detail", style={"marginBottom": "8px", "color": "#495057"}),
            html.Div(id="market-detail", style={
                "backgroundColor": "#f8f9fa", "borderRadius": "8px",
                "padding": "24px", "minHeight": "80px", "color": "#6c757d",
            }, children="Click any point in the scatter plot to inspect a market."),
        ]),
    ]),

    html.Hr(style=DIVIDER),

    # ── Section 2: Feature comparison ──────────────────────────────────────
    html.Div(style=SECTION, children=[
        html.H2("What Makes a Market Attractive", style={"marginBottom": "8px"}),
        html.P(
            "High-attractiveness markets (Cluster 1) differ from baseline markets on every "
            "feature. The strongest signals are trading intensity and average trade size — "
            "consistent with informed traders placing large, well-timed bets. "
            "Trading intensity and average trade size are shown on a log scale to prevent "
            "outliers from dominating the visualization; all other features are on a natural 0–1 scale.",
            style={"color": "#495057", "marginBottom": "24px"},
        ),
        dcc.Graph(figure=make_feature_bars()),
    ]),

    html.Hr(style=DIVIDER),

    html.Div(style=SECTION, children=[
        html.H2("Which Features Matter Most", style={"marginBottom": "8px"}),
        html.P(
            "Logistic regression, random forest, and permutation importance all produced "
            "the same ranking. Wallet concentration, trading intensity, and average trade size "
            "form a leading group — they are correlated with each other (|r| = 0.50–0.74) "
            "but only weakly correlated with raw market volume and trade count (|r| ≤ 0.38), "
            "so the clustering is not simply sorting markets by size. "
            "Error bars show one standard deviation across permutation trials.",
            style={"color": "#495057", "marginBottom": "24px"},
        ),
        dcc.Graph(figure=make_importance_bars()),
    ]),

    html.Hr(style=DIVIDER),

    # ── Section 3: Anomaly table ────────────────────────────────────────────
    html.Div(style=SECTION, children=[
        html.H2("Market Explorer", style={"marginBottom": "8px"}),
        html.P(
            "All 2,310 markets. Sort and filter to explore. "
            "Known insider trading cases are marked ✓. "
            "Anomaly score is only meaningful for Cluster 1 markets — "
            "lower values indicate more unusual behavior within that cluster.",
            style={"color": "#495057", "marginBottom": "24px"},
        ),
        dash_table.DataTable(
            id="anomaly-table",
            columns=[
                {"name": "Question", "id": "question"},
                {"name": "Category", "id": "category"},
                {"name": "Volume", "id": "volume", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=0, symbol=Symbol.yes, symbol_prefix="$", group=Group.yes)},
                {"name": "Uncertainty", "id": "uncertainty", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=2)},
                {"name": "Intensity ($/hr)", "id": "trading_intensity", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=0, symbol=Symbol.yes, symbol_prefix="$", group=Group.yes)},
                {"name": "Avg Trade", "id": "avg_trade_size", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=0, symbol=Symbol.yes, symbol_prefix="$")},
                {"name": "Late Capital", "id": "late_capital_ratio", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=2)},
                {"name": "Wallet Conc.", "id": "top3_wallet_concentration", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=2)},
                {"name": "Velocity", "id": "velocity_ratio",
                "format": Format(scheme=Scheme.fixed, precision=2)},
                {"name": "Score", "id": "anomaly_score", "type": "numeric",
                "format": Format(scheme=Scheme.fixed, precision=4)},
                {"name": "Known", "id": "known"},
            ],
            data=make_anomaly_table_data(),
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left", "padding": "10px 12px",
                "fontSize": "13px", "whiteSpace": "normal", "height": "auto",
            },
            style_header={
                "fontWeight": "600", "backgroundColor": "#f8f9fa",
                "borderBottom": "2px solid #dee2e6",
            },
            style_data_conditional=[
                {"if": {"filter_query": '{known} = "✓"'},
                 "backgroundColor": "#fff9e6", "fontWeight": "500"},
            ],
            page_size=15,
            sort_action="native",
            filter_action="native",
        ),
    ]),

])

# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(
    Output("market-detail", "children"),
    Input("pca-scatter", "clickData"),
)
def show_detail(click_data):
    if not click_data:
        return "Click any point in the scatter plot to inspect a market."

    question = click_data["points"][0]["hovertext"]
    matches = df[df["question"] == question]
    if matches.empty:
        return "Market not found."
    row = matches.iloc[0]

    score = row.get("anomaly_score", 0)
    flag = row.get("anomaly_flag", 1)

    # Comparison bar chart
    display_features = {
        "uncertainty":              "Uncertainty at Open",
        "trading_intensity":        "Trading Intensity ($/hr)",
        "avg_trade_size":           "Avg Trade Size ($)",
        "late_capital_ratio":       "Late Capital Ratio",
        "top3_wallet_concentration":"Wallet Concentration",
        "velocity_ratio":           "Velocity Ratio",
    }

    from sklearn.preprocessing import MinMaxScaler

    c0_means = df[df["cluster"] == 0][list(display_features.keys())].mean()
    c1_means = df[df["cluster"] == 1][list(display_features.keys())].mean()
    this_market = pd.Series({col: float(row[col]) for col in display_features.keys()})

    # Scale using full dataset min/max so extreme individual markets don't blow out the chart
    dataset_min = df[list(display_features.keys())].min()
    dataset_max = df[list(display_features.keys())].max()

    def normalize(series):
        return (series - dataset_min) / (dataset_max - dataset_min)

    c0_scaled = normalize(c0_means)
    c1_scaled = normalize(c1_means)
    this_scaled = normalize(this_market)

    chart_rows = []
    for col, label in display_features.items():
        chart_rows.append({"feature": label, "value": c0_scaled[col], "group": "Cluster 0 — Low"})
        chart_rows.append({"feature": label, "value": c1_scaled[col], "group": "Cluster 1 — High"})
        chart_rows.append({"feature": label, "value": this_scaled[col], "group": "This Market"})

    chart_df = pd.DataFrame(chart_rows)

    fig = px.bar(
        chart_df, x="value", y="feature",
        color="group",
        barmode="group",
        orientation="h",
        color_discrete_map={
            "Cluster 0 — Low":  "#aec6cf",
            "Cluster 1 — High": "#e74c3c",
            "This Market":      "#2c3e50",
        },
        labels={"value": "", "feature": "", "group": ""},
        height=300,
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=20, b=20, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return html.Div([
        html.Div(style={"marginBottom": "12px"}, children=[
            html.Strong(row["question"], style={"fontSize": "1rem"}),
            html.Div(
                f"{row['category']}  ·  Cluster {int(row['cluster'])}  ·  "
                f"${float(row['volume']):,.0f} volume",
                style={"color": "#6c757d", "fontSize": "13px", "marginTop": "4px"}
            ),
            html.Div(f"Trading intensity: ${float(row['trading_intensity']):,.0f}/hr"),
            html.Div(
                f"Anomaly score: {score:.4f}" if flag == -1 else "Not flagged as anomaly",
                style={"color": "#e74c3c" if flag == -1 else "#6c757d",
                       "fontSize": "13px", "fontWeight": "500", "marginTop": "4px"}
            ),
        ]),
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)