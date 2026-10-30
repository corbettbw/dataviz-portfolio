import dash
from dash import html

dash.register_page(__name__, path="/hospital", name="Hospital Readmission")

GITHUB_RAW = "https://raw.githubusercontent.com/corbettbw/hospital-readmission-ml/main/"

SECTION = {"maxWidth": "960px", "margin": "0 auto", "padding": "60px 24px"}
DIVIDER = {"borderTop": "1px solid #e9ecef", "margin": "0"}
HERO_STAT = {
    "textAlign": "center", "padding": "24px",
    "backgroundColor": "#f8f9fa", "borderRadius": "8px",
    "flex": "1", "margin": "0 8px",
}

layout = html.Div(
    style={"fontFamily": "system-ui, sans-serif", "color": "#212529"},
    children=[

        html.Div(style={**SECTION, "paddingTop": "80px"}, children=[
            html.A("← Back", href="/", style={
                "fontSize": "13px", "color": "#6c757d",
                "textDecoration": "none", "display": "block", "marginBottom": "24px",
            }),
            html.H1("30-Day Hospital Readmission Prediction",
                    style={"fontSize": "2.2rem", "fontWeight": "700", "marginBottom": "16px"}),
            html.P(
                "Binary classification models predicting 30-day hospital readmissions "
                "using the UCI Diabetes 130-US Hospitals dataset (~100k patient encounters, "
                "50 features). Logistic Regression and Random Forest achieved nearly identical "
                "discriminative ability, with top predictors including prior inpatient visits, "
                "lab procedures, medications, and length of stay.",
                style={"fontSize": "1.1rem", "color": "#495057", "maxWidth": "720px",
                       "lineHeight": "1.7", "marginBottom": "40px"},
            ),
            html.Div(style={"display": "flex"}, children=[
                html.Div(style=HERO_STAT, children=[
                    html.Div("~100k", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                    html.Div("patient encounters", style={"color": "#6c757d"}),
                ]),
                html.Div(style=HERO_STAT, children=[
                    html.Div("50", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                    html.Div("features", style={"color": "#6c757d"}),
                ]),
                html.Div(style=HERO_STAT, children=[
                    html.Div("0.64", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#e74c3c"}),
                    html.Div("ROC-AUC", style={"color": "#6c757d"}),
                ]),
            ]),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Data Overview", style={"marginBottom": "8px"}),
            html.P(
                "The dataset has significant class imbalance — roughly 88% of encounters "
                "did not result in readmission within 30 days. Key numeric features show "
                "right-skewed distributions typical of clinical utilization data.",
                style={"color": "#495057", "marginBottom": "24px"},
            ),
            html.Img(src=GITHUB_RAW + "eda_distributions.png",
                     style={"width": "100%", "borderRadius": "8px"}),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Model Results", style={"marginBottom": "8px"}),
            html.P(
                "Both models were evaluated on a held-out test set. The Random Forest used "
                "a lowered decision threshold (0.15) to improve recall at the cost of precision — "
                "a reasonable trade-off in a clinical setting where missing a readmission is "
                "more costly than a false alarm.",
                style={"color": "#495057", "marginBottom": "16px"},
            ),
            html.Table(style={"width": "100%", "borderCollapse": "collapse",
                               "fontSize": "14px", "marginBottom": "32px"}, children=[
                html.Thead(children=[
                    html.Tr(children=[
                        html.Th("Model", style={"textAlign": "left", "padding": "10px 12px",
                                                "borderBottom": "2px solid #dee2e6", "fontWeight": "600"}),
                        html.Th("ROC-AUC", style={"padding": "10px 12px",
                                                   "borderBottom": "2px solid #dee2e6", "fontWeight": "600"}),
                        html.Th("Recall (readmitted)", style={"padding": "10px 12px",
                                                               "borderBottom": "2px solid #dee2e6", "fontWeight": "600"}),
                        html.Th("Precision (readmitted)", style={"padding": "10px 12px",
                                                                  "borderBottom": "2px solid #dee2e6", "fontWeight": "600"}),
                    ])
                ]),
                html.Tbody(children=[
                    html.Tr(style={"backgroundColor": "#f8f9fa"}, children=[
                        html.Td("Logistic Regression", style={"padding": "10px 12px"}),
                        html.Td("0.639", style={"padding": "10px 12px", "textAlign": "center"}),
                        html.Td("0.52", style={"padding": "10px 12px", "textAlign": "center"}),
                        html.Td("0.17", style={"padding": "10px 12px", "textAlign": "center"}),
                    ]),
                    html.Tr(children=[
                        html.Td("Random Forest (threshold=0.15)", style={"padding": "10px 12px"}),
                        html.Td("0.640", style={"padding": "10px 12px", "textAlign": "center"}),
                        html.Td("0.43", style={"padding": "10px 12px", "textAlign": "center"}),
                        html.Td("0.19", style={"padding": "10px 12px", "textAlign": "center"}),
                    ]),
                ]),
            ]),
            html.Img(src=GITHUB_RAW + "lr_evaluation.png",
                     style={"width": "100%", "borderRadius": "8px", "marginBottom": "24px"}),
            html.Img(src=GITHUB_RAW + "rf_evaluation.png",
                     style={"width": "100%", "borderRadius": "8px"}),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Feature Importance", style={"marginBottom": "8px"}),
            html.P(
                "Logistic regression coefficients and random forest feature importances "
                "tell complementary stories. LR highlights prior inpatient visits and "
                "medication flags as the strongest linear predictors. RF spreads importance "
                "more broadly across utilization features — lab procedures, medications, "
                "and length of stay dominate.",
                style={"color": "#495057", "marginBottom": "24px"},
            ),
            html.Img(src=GITHUB_RAW + "lr_coefficients.png",
                     style={"width": "100%", "borderRadius": "8px", "marginBottom": "24px"}),
            html.Img(src=GITHUB_RAW + "rf_feature_importance.png",
                     style={"width": "100%", "borderRadius": "8px"}),
        ]),

        html.Hr(style=DIVIDER),

        html.Div(style=SECTION, children=[
            html.H2("Skills Demonstrated", style={"marginBottom": "16px"}),
            html.Ul(style={"color": "#495057", "lineHeight": "2", "paddingLeft": "20px"}, children=[
                html.Li("Clinical data cleaning and feature engineering (ICD-9 code recoding, polypharmacy flagging)"),
                html.Li("EDA with class imbalance analysis"),
                html.Li("Binary classification: Logistic Regression and Random Forest"),
                html.Li("Threshold tuning for recall optimization in an imbalanced clinical context"),
                html.Li("Model evaluation: ROC-AUC, confusion matrix, feature importance, coefficient analysis"),
            ]),
            html.A("View on GitHub →",
                   href="https://github.com/corbettbw/hospital-readmission-ml",
                   target="_blank",
                   style={"display": "inline-block", "marginTop": "16px",
                          "color": "#0077cc", "fontSize": "14px"}),
        ]),
    ]
)