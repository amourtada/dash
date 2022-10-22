# %%
import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

#Each library provides a building block for your application:

# dash helps you initialize your application.
# dash_core_components (dcc) allows you to create interactive components like graphs, dropdowns, or date ranges
# dash_html_components lets you access HTML tags
# pandas helps you read and organize the data

# Create an empty file named app.py in the root directory of your project, then review the code of app.py in this section
data = pd.read_csv("avocado.csv")
#data = data.query("type == 'conventional' and region == 'Albany'")
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values("Date", inplace=True)

# Create an instance of the Dash class with external style sheets, and specify app title
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"                     # specify an external CSS file, a font family, that you want to load in your application
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"               # This is the text that appears in the title bar of web browser
server = app.server

# %%
# Defining the Layout of Your Dash Application
# Define the layout property of your application. This property dictates the look of your app. 
# you’ll use a heading with a description below it and two graphs. Here’s how you define it:

# Define the parent component, an html.Div. Then, add two more elements, a heading (html.H1) and a paragraph (html.P), as its children.
# These components are equivalent to the div, h1, and p HTML tags. You can use the components’ arguments to modify attributes or the content of the tags. 
# For example, to specify what goes inside the div tag, you use the children argument in html.Div
# There are also other arguments in the components, such as style, className, or id, that refer to attributes of the HTML tags

# Part of the layout shown on lines enclosed with html-1 will get transformed into the following HTML code
# <div>
#   <h1>Avocado Analytics</h1>
#   <p>
#     Analyze the behavior of avocado prices and the number
#     of avocados sold in the US between 2015 and 2018
#   </p>
#   <!-- Rest of the app -->
# </div>

# On lines enclosed with html-2 in the layout code snippet, these are graph component from Dash Core Components
# Under the hood, Dash uses Plotly.js to generate graphs. The dcc.Graph components expect a figure object or
# a Python dictionary containing the plot’s data and layout (lines enclosed with html-2-0)

# app.layout = html.Div(                               # html-1
#     children=[
#         # html.H1(children="Avocado Analytics", style={"fontSize": "48px", "color": "red"}), 
#         html.H1(children="Avocado Analytics",  className="header-title"),
#         html.P(
#             children="Analyze the behavior of avocado prices"
#             " and the number of avocados sold in the US"
#             " between 2015 and 2018",
#         ),                                        # html-1


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="Avocado Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the behavior of avocado prices"
                    " and the number of avocados sold in the US"
                    " between 2015 and 2018",
                    className="header-description",
                )
            ],
            className="header",
        ),                                          # html-1
        # dcc.Graph(                                  # html-2 or html-2-0
        #     figure={
        #         "data": [
        #             {                               # html-2
        #                 "x": data["Date"],
        #                 "y": data["AveragePrice"],
        #                 "type": "lines",
        #             },
        #         ],
        #         "layout": {"title": "Average Price of Avocados"},
        #     },
        # ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in np.sort(data.region.unique())
                            ],
                            value="Albany",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": avocado_type, "value": avocado_type}
                                for avocado_type in data.type.unique()
                            ],
                            value="organic",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


# %%
@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(region, avocado_type, start_date, end_date):
    mask = (
        (data.region == region)
        & (data.type == avocado_type)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["AveragePrice"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of Avocados",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Total Volume"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Avocados Sold", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure

# %%
# The following two lines of code help you run your application
if __name__ == "__main__":
    #app.run_server(debug=True)
    app.run_server(debug=True, use_reloader=False)


