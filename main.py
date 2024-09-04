import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, MATCH
import plotly.express as px
import pandas as pd
import urllib.parse

# Load your Excel data
data_path =  'data_path =  'Scorecards_final.xlsx''
df = pd.read_excel(data_path)

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Sidebar layout with navigation links
sidebar = html.Div(
    [
        html.H2("Navigation", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact"),
            ] + [
                dbc.NavLink(scorecard, href=f"/{urllib.parse.quote(scorecard)}", active="exact") for scorecard in
                df['Scorecard name'].unique()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={"position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "340px", "padding": "20px",
           "background-color": "#010103", "color": "#ffffff"},
)

# Layout for the Overview page
overview_layout = html.Div([
    html.H1('Overview', style={"color": "#ffffff"}),
    dcc.Graph(id='overview-bar-chart'),
    html.Hr(),
    html.Div(id='overview-table-container')
], style={"margin-left": "360px", "padding": "20px", "background-color": "#010103", "color": "#ffffff"})


# Layout for each Scorecard page
def scorecard_layout(scorecard_name):
    return html.Div([
        html.H1(f'{scorecard_name} Scorecard', style={"color": "#ffffff"}),
        dcc.Graph(id={'type': 'scorecard-bar-chart', 'index': scorecard_name}),
        html.Hr(),
        html.Div(id={'type': 'scorecard-table-container', 'index': scorecard_name})
    ], style={"margin-left": "360px", "padding": "20px", "background-color": "#010103", "color": "#ffffff"})


# Main layout including sidebar and page content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id='page-content')
])


# Callback to update the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    decoded_pathname = urllib.parse.unquote(pathname)

    if decoded_pathname == '/':
        return overview_layout
    scorecard_name = decoded_pathname[1:]
    if scorecard_name in df['Scorecard name'].unique():
        return scorecard_layout(scorecard_name)
    return html.Div("404: Page not found", style={"color": "red"})


# Callback to update the Overview page's bar chart
@app.callback(
    Output('overview-bar-chart', 'figure'),
    [Input('url', 'pathname')]
)
def update_overview_chart(pathname):
    fig = px.bar(
        df,
        y='IMS year',
        x='IMS status',
        color='IMS status',
        orientation='h',
        custom_data=['IMS status'],
        barmode='stack',
        color_discrete_map={
            "Missing Minimum Requirements": "red",
            "Approaches Minimum Requirements": "lightcoral",
            "Meets Minimum Requirements": "lightorange",
            "Exceeds Minimum Requirements": "lightgreen",
            "Getting ready": "red",
            "Moving forward": "lightcoral",
            "At milestone": "lightgreen"
        }
    )
    fig.update_layout(title="Number of IMS Status per Year for All Scorecards", title_x=0.5, paper_bgcolor="#010103",
                      plot_bgcolor="#010103", font_color="#ffffff")
    return fig


# Callback to update the table based on the Overview bar chart selection
@app.callback(
    Output('overview-table-container', 'children'),
    [Input('overview-bar-chart', 'clickData')]
)
def update_overview_table(click_data):
    if click_data:
        selected_year = click_data['points'][0]['y']
        selected_status = click_data['points'][0]['customdata'][0] if 'customdata' in click_data['points'][0] else None

        filtered_df = df[
            (df['IMS year'] == selected_year) &
            (df['IMS status'] == selected_status)
            ]

        if filtered_df.empty:
            return html.Div("No matching data found.", style={"color": "red"})

        return dbc.Table.from_dataframe(filtered_df, striped=True, bordered=True, hover=True, dark=True)
    else:
        return html.Div("Please select a point on the chart to see the details.", style={"color": "#ffffff"})


# Callback to update the bar chart and table for each scorecard
@app.callback(
    [Output({'type': 'scorecard-bar-chart', 'index': MATCH}, 'figure'),
     Output({'type': 'scorecard-table-container', 'index': MATCH}, 'children')],
    [Input('url', 'pathname'),
     Input({'type': 'scorecard-bar-chart', 'index': MATCH}, 'clickData')]
)
def update_scorecard_page(pathname, click_data):
    decoded_pathname = urllib.parse.unquote(pathname)
    scorecard_name = decoded_pathname[1:]

    if scorecard_name in df['Scorecard name'].unique():
        filtered_df = df[df['Scorecard name'] == scorecard_name]

        fig = px.bar(
            filtered_df,
            y='IMS year',
            x='IMS status',
            color='IMS status',
            orientation='h',
            custom_data=['IMS status'],
            barmode='stack',
            color_discrete_map={
                "Missing Minimum Requirements": "red",
                "Approaches Minimum Requirements": "lightcoral",
                "Meets Minimum Requirements": "lightorange",
                "Exceeds Minimum Requirements": "lightgreen",
                "Getting ready": "red",
                "Moving forward": "lightcoral",
                "At milestone": "lightgreen"
            }
        )
        fig.update_layout(title=f"Number of IMS Status per Year for {scorecard_name}", title_x=0.5,
                          paper_bgcolor="#010103", plot_bgcolor="#010103", font_color="#ffffff")

        if click_data:
            selected_year = click_data['points'][0]['y']
            selected_status = click_data['points'][0]['customdata'][0] if 'customdata' in click_data['points'][
                0] else None

            filtered_table_df = filtered_df[
                (filtered_df['IMS year'] == selected_year) &
                (filtered_df['IMS status'] == selected_status)
                ]

            if filtered_table_df.empty:
                table_container = html.Div("No matching data found.", style={"color": "red"})
            else:
                table_container = dbc.Table.from_dataframe(filtered_table_df, striped=True, bordered=True, hover=True,
                                                           dark=True)
        else:
            table_container = html.Div("Please select a point on the chart to see the details.",
                                       style={"color": "#ffffff"})

        return fig, table_container

    return {}, html.Div("Invalid Scorecard", style={"color": "red"})


# Run the app
# Run the app on port 8057
if __name__ == '__main__':
    app.run_server(debug=True, port=8057)
