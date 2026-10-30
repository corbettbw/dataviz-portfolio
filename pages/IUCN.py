import dash
from dash import html, dcc, dash_table, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.request, json as _json, urllib.parse
import json as _json
import urllib.parse

dash.register_page(__name__, path="/iucn", name="Marine Mammals")

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
BASE = "https://raw.githubusercontent.com/corbettbw/jupyter-portfolio/main/"

def load_data():
    try:
        species = pd.read_csv(BASE + "Species.csv")
        genus   = pd.read_csv(BASE + "Genus.csv",   encoding="utf-8-sig")
        country = pd.read_csv(BASE + "Country.csv", encoding="utf-8-sig")

        # "AO Angola" → country_name="Angola"
        country["country_name"] = country["country"].str.split(" ", n=1).str[1]

        df = species.merge(genus, on="genus_name", how="left")
        df["display_name"] = df["genus_name"] + " " + df["species_name"]

        return df, country
    except Exception as e:
        print(f"Could not load IUCN data: {e}")
        return pd.DataFrame(), pd.DataFrame()

df, country_df = load_data()

# ---------------------------------------------------------------------------
# Threat category config
# ---------------------------------------------------------------------------
CAT_ORDER  = ["EX", "CR", "EN", "VU", "NT", "DD", "LC"]
CAT_LABELS = {
    "EX": "Extinct",
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "VU": "Vulnerable",
    "NT": "Near Threatened",
    "DD": "Data Deficient",
    "LC": "Least Concern",
}
CAT_COLORS = {
    "EX": "#2c2c2c",
    "CR": "#cc0000",
    "EN": "#e74c3c",
    "VU": "#e67e22",
    "NT": "#f1c40f",
    "DD": "#95a5a6",
    "LC": "#2ecc71",
}

# ---------------------------------------------------------------------------
# Derived summary values
# ---------------------------------------------------------------------------
n_species    = len(df)
n_threatened = int(df["category"].isin(["CR", "EN", "VU"]).sum())
n_extinct    = int((df["category"] == "EX").sum())

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
SECTION   = {"maxWidth": "960px", "margin": "0 auto", "padding": "40px 24px"}
HERO_STAT = {
    "textAlign": "center", "padding": "24px",
    "backgroundColor": "#f8f9fa", "borderRadius": "8px",
    "flex": "1", "margin": "0 8px",
}
DIVIDER = {"borderTop": "1px solid #e9ecef", "margin": "0"}

# ---------------------------------------------------------------------------
# Static figure
# ---------------------------------------------------------------------------
def make_category_chart():
    counts = (
        df.groupby("category")
        .size()
        .reindex(CAT_ORDER)
        .fillna(0)
        .reset_index(name="count")
    )
    counts["label"] = counts["category"].map(CAT_LABELS)
    fig = px.bar(
        counts, x="label", y="count",
        color="category",
        color_discrete_map=CAT_COLORS,
        labels={"label": "", "count": "Species", "category": ""},
        height=280,
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        margin=dict(t=20, b=20),
        xaxis=dict(
            categoryorder="array",
            categoryarray=[CAT_LABELS[c] for c in CAT_ORDER],
        ),
    )
    return fig

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
layout = html.Div(
    style={"fontFamily": "system-ui, sans-serif", "color": "#212529"},
    children=[

        html.Div(style={**SECTION, "paddingTop": "60px"}, children=[
            html.H1("Marine Mammal Conservation Status",
                    style={"fontSize": "2rem", "fontWeight": "700",
                           "marginBottom": "12px"}),
            html.P(
                "IUCN Red List assessments for 187 marine mammal species worldwide. "
                "Select a species from the table to see its geographic range.",
                style={"color": "#495057", "marginBottom": "32px"},
            ),
            html.Div(style={"display": "flex"}, children=[
                html.Div(style=HERO_STAT, children=[
                    html.Div(str(n_species),
                             style={"fontSize": "2.5rem", "fontWeight": "700",
                                    "color": "#e74c3c"}),
                    html.Div("species assessed", style={"color": "#6c757d"}),
                ]),
                html.Div(style=HERO_STAT, children=[
                    html.Div(str(n_threatened),
                             style={"fontSize": "2.5rem", "fontWeight": "700",
                                    "color": "#e74c3c"}),
                    html.Div("threatened (CR/EN/VU)", style={"color": "#6c757d"}),
                ]),
                html.Div(style=HERO_STAT, children=[
                    html.Div(str(n_extinct),
                             style={"fontSize": "2.5rem", "fontWeight": "700",
                                    "color": "#2c2c2c"}),
                    html.Div("extinct", style={"color": "#6c757d"}),
                ]),
            ]),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Status Distribution", style={"marginBottom": "8px"}),
            dcc.Graph(figure=make_category_chart(),
                      config={"displayModeBar": False}),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Species Explorer", style={"marginBottom": "8px"}),
            html.P(
                "Click any row to see that species' range on the map below.",
                style={"color": "#495057", "marginBottom": "16px"},
            ),
            dash_table.DataTable(
                id="iucn-species-table",
                columns=[
                    {"name": "Scientific Name", "id": "display_name"},
                    {"name": "Family",          "id": "family_name"},
                    {"name": "Status",          "id": "category"},
                ],
                data=(
                    df[["taxonid", "display_name", "family_name", "category"]]
                    .sort_values(["category", "family_name"])
                    .to_dict("records")
                ),
                row_selectable="single",
                selected_rows=[],
                filter_action="native",
                sort_action="native",
                page_size=20,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left", "padding": "8px 12px",
                    "fontSize": "13px",
                },
                style_header={
                    "fontWeight": "600", "backgroundColor": "#f8f9fa",
                    "borderBottom": "2px solid #dee2e6",
                },
                style_data_conditional=[
                    {"if": {"filter_query": "{category} = 'CR'"},
                     "backgroundColor": "#fff0f0"},
                    {"if": {"filter_query": "{category} = 'EN'"},
                     "backgroundColor": "#fff5f0"},
                    {"if": {"filter_query": "{category} = 'EX'"},
                     "backgroundColor": "#f0f0f0", "color": "#666"},
                    {"if": {"row_index": "odd"},
                     "backgroundColor": "#fafafa"},
                ],
            ),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.Div(id="iucn-map-title", style={
                "fontSize": "1rem", "fontWeight": "600",
                "color": "#495057", "marginBottom": "8px",
                "minHeight": "24px",
            }),
            html.Div(id="iucn-species-info", style={"marginBottom": "16px"}),
            dcc.Graph(id="iucn-map", config={"displayModeBar": False}),
        ]),
    ]
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
GEO_LAYOUT = dict(
    geo=dict(showframe=False, showcoastlines=True,
             projection_type="natural earth"),
    margin=dict(t=0, b=0, l=0, r=0),
    paper_bgcolor="white",
    height=450,
)

def empty_map():
    fig = go.Figure(go.Choropleth())
    fig.update_layout(**GEO_LAYOUT)
    return fig

# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------
@callback(
    Output("iucn-map", "figure"),
    Output("iucn-map-title", "children"),
    Output("iucn-species-info", "children"),
    Input("iucn-species-table", "selected_rows"),
    Input("iucn-species-table", "derived_virtual_data"),
)
def update_map(selected_rows, virtual_data):
    species_info = None  # default: no info panel

    if not selected_rows or virtual_data is None:
        threatened_ids = df[df["category"].isin(["CR", "EN", "VU"])]["taxonid"].tolist()
        subset = country_df[country_df["taxonid"].isin(threatened_ids)]
        title = "Range: all threatened species (CR/EN/VU)"
        if subset.empty:
            return empty_map(), title, None
        counts = subset.groupby("country_name").size().reset_index(name="count")
        fig = px.choropleth(
            counts,
            locations="country_name",
            locationmode="country names",
            color="count",
            color_continuous_scale=[[0, "#fee0d2"], [1, "#cb1a1a"]],
            labels={"count": "Threatened species"},
            height=450,
        )
    else:
        row = virtual_data[selected_rows[0]]
        taxonid = row["taxonid"]
        species_row = df[df["taxonid"] == taxonid].iloc[0]
        subset = country_df[country_df["taxonid"] == taxonid].copy()
        status = CAT_LABELS.get(species_row["category"], species_row["category"])
        display = row["display_name"]
        title = f"{display} — {status}"

        # Fetch Wikipedia summary
        wiki_name = urllib.parse.quote(display.replace(" ", "_"))
        print("WIKI URL:", f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}")
        try:
            req = urllib.request.Request(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}",
                headers={"User-Agent": "dataviz-portfolio/1.0 (corbettbw@gmail.com)"},
            )
            response = urllib.request.urlopen(req, timeout=4)
            wiki = _json.loads(response.read())
            
            thumb = wiki.get("thumbnail", {}).get("source")
            extract = wiki.get("extract", "")
            wiki_url = wiki.get("content_urls", {}).get("desktop", {}).get("page", "#")

            info_children = []
            if thumb or extract:
                if thumb:
                    info_children.append(
                        html.Img(src=thumb, style={
                            "float": "right", "marginLeft": "16px",
                            "marginBottom": "8px", "borderRadius": "6px",
                            "maxHeight": "180px", "maxWidth": "240px",
                        })
                    )
                if extract:
                    info_children.append(html.P(extract, style={
                        "color": "#495057", "fontSize": "14px",
                        "lineHeight": "1.6", "margin": "0",
                    }))
                info_children.append(html.Div(style={"clear": "both"}))
                info_children.append(
                    html.A("→ Wikipedia", href=wiki_url, target="_blank",
                           style={"fontSize": "13px", "color": "#0077cc"})
                )
                species_info = html.Div(info_children, style={
                    "padding": "16px",
                    "backgroundColor": "#f8f9fa",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                })
        except Exception as e:
            print("WIKI ERROR:", e)
            
        if subset.empty:
            return empty_map(), title, species_info
        country_list = subset[["country_name"]].drop_duplicates().copy()
        country_list["present"] = 1
        fig = px.choropleth(
            country_list,
            locations="country_name",
            locationmode="country names",
            color="present",
            color_continuous_scale=[[0, "#e74c3c"], [1, "#e74c3c"]],
            height=450,
        )
        fig.update_coloraxes(showscale=False)

    fig.update_layout(**GEO_LAYOUT)
    return fig, title, species_info