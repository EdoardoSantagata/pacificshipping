import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
from dash.dash_table import DataTable
# Helper functions for regression-based DWT estimation
from sklearn.linear_model import LinearRegression
import numpy as np
import dash
import time
from dash.exceptions import PreventUpdate


# File and sheet details
excel_file = "Pacific Shipping Database - FINAL (for paper).xlsx"
sheet_name = "COMPLETE - Data Handle"

# Read the data from the Excel file
data = pd.read_excel(excel_file, sheet_name=sheet_name)

#%%%%%%%%%%%%%%%%%%FUEL_CONSUMPTION_ANALYSIS%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Create a processed copy of the original dataset for SFC Analysis
processed_data = data.copy()

# Add Operational Days to both datasets
processed_data["Operational Days"] = 0.8 * 365  # Default operational days
data["Operational Days"] = 0.8 * 365  # Default operational days

# Fill missing average speed with the dataset-wide average
processed_data["Average Speed"] = processed_data["Average Speed"].fillna(data["Average Speed"].mean())


# Helper function for regression-based DWT estimation
from sklearn.linear_model import LinearRegression
import numpy as np

def estimate_dwt(row, data):
    """Estimate DWT based on available parameters using regression analysis."""
    if pd.notnull(row["Capacity - Dwt"]):  # If DWT exists, no need to estimate
        return row["Capacity - Dwt"]
    
    # Select the appropriate subset based on vessel type
    vessel_category = row["Vessel Type - Contextual"]
    subset = data[data["Vessel Type - Contextual"] == vessel_category]
    
    # Remove rows missing required variables for regression
    subset = subset.dropna(subset=["Capacity - Dwt", "Capacity - Gt", "Length", "Draught"])
    X, y = None, subset["Capacity - Dwt"]

    # Regression scenarios
    if pd.notnull(row["Capacity - Gt"]) and pd.notnull(row["Length"]) and pd.notnull(row["Draught"]):
        X = subset[["Capacity - Gt", "Length", "Draught"]]
    elif pd.notnull(row["Capacity - Gt"]) and pd.notnull(row["Length"]):
        X = subset[["Capacity - Gt", "Length"]]
    elif pd.notnull(row["Capacity - Gt"]) and pd.notnull(row["Draught"]):
        X = subset[["Capacity - Gt", "Draught"]]
    elif pd.notnull(row["Length"]) and pd.notnull(row["Draught"]):
        X = subset[["Length", "Draught"]]
    elif pd.notnull(row["Capacity - Gt"]):
        X = subset[["Capacity - Gt"]]
    elif pd.notnull(row["Length"]):
        X = subset[["Length"]]
    elif pd.notnull(row["Draught"]):
        X = subset[["Draught"]]

    # Perform regression if data is available
    if X is not None and len(X) > 1:
        model = LinearRegression()
        model.fit(X, y)
        test_features = np.array([row[col] for col in X.columns]).reshape(1, -1)
        return model.predict(test_features)[0]
    else:
        return subset["Capacity - Dwt"].mean()  # Use mean DWT as a fallback

# Estimate DWT for processed data
processed_data["Estimated DWT"] = processed_data.apply(estimate_dwt, axis=1, data=processed_data)

# Calculate ship fuel consumption
def calculate_fuel_consumption(row):
    """Calculate fuel consumption for a given ship."""
    dwt = row["Estimated DWT"]
    avg_speed = row["Average Speed"]
    operational_days = row["Operational Days"]
    return (1 / 120000) * (dwt**(2 / 3)) * (avg_speed**3) * operational_days

processed_data["Fuel Consumption"] = processed_data.apply(calculate_fuel_consumption, axis=1)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Add Vessel Type - Simplified categorization
simplified_mapping = {
    "General Cargo": "Cargo Vessels",
    "Container Ship": "Cargo Vessels",
    "Bulk Carrier": "Cargo Vessels",
    "Reefer": "Cargo Vessels",
    "Special Cargo": "Cargo Vessels",
    "Heavy Load Carrier": "Cargo Vessels",
    "Other Cargo": "Cargo Vessels",
    "Crude Oil Tanker": "Tankers",
    "Oil Products Tanker": "Tankers",
    "Oil/Chemical Tanker": "Tankers",
    "LNG Tanker": "Tankers",
    "LPG Tanker": "Tankers",
    "Passenger Vessel": "Passenger Vessels",
    "Other Passenger": "Passenger Vessels",
    "Special Passenger Vessel": "Passenger Vessels",
    "Ro-Ro/Passenger Vessel": "Mixed Vessels",
    "Ro-Ro/Vehicles Carrier": "Mixed Vessels",
    "Passenger/Cargo Ship": "Mixed Vessels",
    "Special Craft": "Specialized Vessels",
    "Other Special Craft": "Specialized Vessels",
    "Supply Vessel": "Specialized Vessels",
    "Landing Craft": "Specialized Vessels",
}

data["Vessel Type - Simplified"] = data["Vessel Type - Detailed"].map(simplified_mapping)
processed_data["Vessel Type - Simplified"] = processed_data["Vessel Type - Detailed"].map(simplified_mapping)

# Add Vessel Type - Contextual categorization
contextual_categories = {
    "LNG Tanker": "LNG Tanker",
    "Passenger Vessel": "Passenger Vessel",
    "Ro-Ro/Vehicles Carrier": "Ro-Ro/Vehicles Carrier",
    "Special Craft": "Special Craft",
    "Special Passenger Vessel": "Special Passenger Vessel",
    # Map all remaining vessel types to "Rest"
    "General Cargo": "Rest",
    "Container Ship": "Rest",
    "Bulk Carrier": "Rest",
    "Reefer": "Rest",
    "Special Cargo": "Rest",
    "Heavy Load Carrier": "Rest",
    "Other Cargo": "Rest",
    "Crude Oil Tanker": "Rest",
    "Oil Products Tanker": "Rest",
    "Oil/Chemical Tanker": "Rest",
    "LPG Tanker": "Rest",
    "Other Passenger": "Rest",
    "Passenger/Cargo Ship": "Rest",
    "Ro-Ro/Passenger Vessel": "Rest",
    "Other Special Craft": "Rest",
    "Supply Vessel": "Rest",
    "Landing Craft": "Rest",
}

data["Vessel Type - Contextual"] = data["Vessel Type - Detailed"].map(contextual_categories)

#%%%%%%%%%%%%%%%%%%
# Add Vessel Type - Contextual categorization
processed_data["Vessel Type - Contextual"] = processed_data["Vessel Type - Detailed"].map(contextual_categories)
#&&&&&&&&&&&&&&&&&&&

# Define PICTs and categorization
PICTs = [
    "American Samoa", "Cook Is", "Fiji", "French Polynesia", "Guam", "Kiribati", "Marshall Is",
    "Micronesia", "Nauru", "New Caledonia", "Niue", "N Mariana Is", "Palau", "Papua New Guinea",
    "Pitcairn Is", "Samoa", "Solomon Islands", "Tokelau", "Tonga", "Tuvalu", "Vanuatu", "Wallis Futuna Is"
]

def categorize_flag(flag, mode):
    if mode == "Pacific - Simplified":
        return "PICTs" if flag in PICTs else "Other"
    elif mode == "Pacific - Detailed":
        return flag if flag in PICTs else "Other"
    elif mode == "Pacific Only":
        return flag if flag in PICTs else None
    elif mode == "Other Only":
        return None if flag in PICTs else flag
    return flag  # Default: All Countries

# Map the dropdown selection to the relevant column
def get_column_from_categorization(categorization):
    if categorization.startswith("Vessel Type"):
        return categorization  # Maps directly to a vessel type column
    return "Flag"  # Default to Flag for country-based categorization

# App initialization with suppress_callback_exceptions=True
app = Dash(__name__, suppress_callback_exceptions=True)

# Helper functions for layouts
def vessel_plots_page():
    return html.Div([
        html.H1("Vessel Plots"),
        html.Div([
            html.H3("Categorization and Variable Selection"),
            dcc.Dropdown(
                id="categorization-dropdown",
                options=[
                    {"label": "Vessel Type - Detailed", "value": "Vessel Type - Detailed"},
                    {"label": "Vessel Type - Generic", "value": "Vessel Type - Generic"},
                    {"label": "Vessel Type - Simplified", "value": "Vessel Type - Simplified"},
                    {"label": "Vessel Type - Contextual", "value": "Vessel Type - Contextual"},
                    {"label": "All Countries", "value": "All Countries"},
                    {"label": "Pacific - Simplified", "value": "Pacific - Simplified"},
                    {"label": "Pacific - Detailed", "value": "Pacific - Detailed"},
                    {"label": "Pacific Only", "value": "Pacific Only"},
                    {"label": "Other Only", "value": "Other Only"},
                ],
                value="Vessel Type - Detailed",
                clearable=False,
            ),
        ]),

        html.Div([
            html.H3("Scatter Plot Variables"),
            dcc.Dropdown(
                id="scatter-x-dropdown",
                options=[
                    {"label": "DWT (Deadweight Tonnage)", "value": "Capacity - Dwt"},
                    {"label": "GT (Gross Tonnage)", "value": "Capacity - Gt"},
                    {"label": "Length", "value": "Length"},
                    {"label": "Draught", "value": "Draught"},
                    {"label": "Average Speed", "value": "Average Speed"},
                ],
                value="Capacity - Dwt",
                clearable=False,
            ),
            dcc.Dropdown(
                id="scatter-y-dropdown",
                options=[
                    {"label": "DWT (Deadweight Tonnage)", "value": "Capacity - Dwt"},
                    {"label": "GT (Gross Tonnage)", "value": "Capacity - Gt"},
                    {"label": "Length", "value": "Length"},
                    {"label": "Draught", "value": "Draught"},
                    {"label": "Average Speed", "value": "Average Speed"},
                ],
                value="Capacity - Gt",
                clearable=False,
            ),
            dcc.Graph(id="scatter-plot"),
        ]),

        html.Div([
            html.H3("Histogram Variable"),
            dcc.Dropdown(
                id="histogram-variable-dropdown",
                options=[
                    {"label": "DWT (Deadweight Tonnage)", "value": "Capacity - Dwt"},
                    {"label": "GT (Gross Tonnage)", "value": "Capacity - Gt"},
                    {"label": "Length", "value": "Length"},
                    {"label": "Draught", "value": "Draught"},
                    {"label": "Average Speed", "value": "Average Speed"},
                ],
                value="Capacity - Dwt",
                clearable=False,
            ),
            dcc.Graph(id="histogram"),
        ]),

        html.Div([
            html.H3("Bar Chart"),
            dcc.Graph(id="bar-chart"),
        ]),

        html.Div([
            html.H3("Pie Chart"),
            dcc.Graph(id="pie-chart"),
        ]),

        #dcc.Link("Go to Vessel Statistics", href="/vessel-statistics"),
    ])

def vessel_statistics_page():
    return html.Div([
        html.H1("Vessel Statistics"),
        dcc.Dropdown(
            id="categorization-dropdown",
            options=[
                {"label": "Vessel Type - Detailed", "value": "Vessel Type - Detailed"},
                {"label": "Vessel Type - Generic", "value": "Vessel Type - Generic"},
                {"label": "Vessel Type - Simplified", "value": "Vessel Type - Simplified"},
                {"label": "Vessel Type - Contextual", "value": "Vessel Type - Contextual"},
                {"label": "All Countries", "value": "All Countries"},
                {"label": "Pacific - Simplified", "value": "Pacific - Simplified"},
                {"label": "Pacific - Detailed", "value": "Pacific - Detailed"},
                {"label": "Pacific Only", "value": "Pacific Only"},
                {"label": "Other Only", "value": "Other Only"},
            ],
            value="Vessel Type - Detailed",
            clearable=False,
        ),
        html.Div(id="vessel-statistics-output"),
        #dcc.Link("Go to Vessel Plots", href="/vessel-plots"),
    ])

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def sfc_analysis_page():
    return html.Div([
        html.H1("SFC Analysis"),
        html.Div([
            html.H3("Histogram of Ship Fuel Consumption"),
            dcc.Dropdown(
                id="sfc-categorization-dropdown",
                options=[
                    {"label": "Vessel Type - Detailed", "value": "Vessel Type - Detailed"},
                    {"label": "Vessel Type - Generic", "value": "Vessel Type - Generic"},
                    {"label": "Vessel Type - Simplified", "value": "Vessel Type - Simplified"},
                    {"label": "Vessel Type - Contextual", "value": "Vessel Type - Contextual"},
                    {"label": "All Countries", "value": "All Countries"},
                    {"label": "Pacific - Simplified", "value": "Pacific - Simplified"},
                    {"label": "Pacific - Detailed", "value": "Pacific - Detailed"},
                    {"label": "Pacific Only", "value": "Pacific Only"},
                    {"label": "Other Only", "value": "Other Only"},
                ],
                value="Vessel Type - Contextual",
                clearable=False,
            ),
            dcc.Graph(id="sfc-histogram"),
        ]),
        # Fuel Type Allocation Inputs
        html.Div([
            html.H3("Allocate Fuel Type Percentages"),
            html.Div([
                dcc.Input(id="hfo-input", type="number", placeholder="HFO (%)", value=52, min=0, max=100, step=1, style={"margin-right": "10px"}),
                dcc.Input(id="lfo-input", type="number", placeholder="LFO (%)", value=31, min=0, max=100, step=1, style={"margin-right": "10px"}),
                dcc.Input(id="mdo/mgo-input", type="number", placeholder="MDO/MGO (%)", value=12, min=0, max=100, step=1, style={"margin-right": "10px"}),
                dcc.Input(id="lng-input", type="number", placeholder="LNG (%)", value=5, min=0, max=100, step=1),
            ], style={"display": "flex", "justify-content": "center", "margin-bottom": "20px"}),
            html.Div(id="allocation-warning", style={"color": "red", "text-align": "center", "margin-bottom": "20px"}),
        ]),

        # Pie Chart for Fuel Allocation
        html.Div([
            html.H3("Fuel Type Allocation"),
            dcc.Graph(id="fuel-allocation-pie-chart"),
        ], style={"margin-bottom": "20px"}),


        # Total Fuel Consumption Output
        html.Div([
            html.H3("Total Fuel Consumption (Tonnes)"),
            html.Div(id="total-fuel-consumption", style={"font-size": "20px", "text-align": "center", "margin-bottom": "20px"}),
        ]),

        html.Div([
            html.H3("Fuel Consumption by Category (Tonnes)"),
            dcc.Graph(id="fuel-consumption-category-bar-chart"),
        ], style={"margin-bottom": "20px"}),

        html.Div([
            html.H3("Fuel Consumption in TJ by Fuel Type"),
            dcc.Graph(id="fuel-consumption-bar-chart"),
        ], style={"margin-bottom": "20px"}),

        html.Div([
            html.H3("Summary Table of Missing Data"),
            DataTable(
                id="sfc-summary-table",
                style_table={"overflowX": "auto"},
            ),
        ]),
        dcc.Link("Go to Vessel Plots", href="/vessel-plots", style={"margin-right": "20px"}),
        dcc.Link("Go to Vessel Statistics", href="/vessel-statistics"),
    ])
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# LAYOUT FOR TOOL ----------------NAVIGATION BAR
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="fuel-consumption-data", storage_type="memory"),  # TO STORE FUEL CONSUMPTION RESULTS
    html.Div([
        html.Div([
            html.H1("Pacific Shipping Database Analysis Tool"),
            html.Div([
                dcc.Link("Vessel Plots", href="/vessel-plots", style={"margin-right": "20px"}),
                dcc.Link("Vessel Statistics", href="/vessel-statistics", style={"margin-right": "20px"}),
                dcc.Link("Database Inspector", href="/database-inspector"),
                dcc.Link("SFC Analysis", href="/sfc-analysis", style={"margin-left": "20px"}),
                dcc.Link("Decarbonisation Scenarios", href="/decarbonisation-scenarios", style={"margin-left": "20px"}),
            ], style={"text-align": "center", "margin-bottom": "20px"}),
        ], style={"background-color": "#f8f9fa", "padding": "10px", "box-shadow": "0px 4px 2px -2px gray"}),
    ]),
    html.Div(id="page-content"),
])
#-----------------------------------

@app.callback(
    Output("scatter-plot", "figure"),
    [
        Input("categorization-dropdown", "value"),
        Input("scatter-x-dropdown", "value"),
        Input("scatter-y-dropdown", "value"),
    ]
)
def update_scatter_plot(categorization, x_var, y_var):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    fig = px.scatter(
        filtered_data,
        x=x_var,
        y=y_var,
        color=column,
        title=f"Scatter Plot: {x_var} vs {y_var} ({categorization})"
    )
    return fig

@app.callback(
    Output("histogram", "figure"),
    [
        Input("categorization-dropdown", "value"),
        Input("histogram-variable-dropdown", "value"),
    ]
)
def update_histogram(categorization, variable):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    # Exclude rows where the histogram variable has NaN or is 0
    filtered_data = filtered_data[filtered_data[variable].notnull() & (filtered_data[variable] > 0)]

    fig = px.histogram(
        filtered_data,
        x=variable,
        color=column,
        title=f"Histogram: {variable} ({categorization})"
    )
    return fig

@app.callback(
    Output("bar-chart", "figure"),
    [Input("categorization-dropdown", "value")]
)
def update_bar_chart(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    fig = px.bar(
        filtered_data,
        x=column,
        title="Number of Vessels per Category",
        labels={column: categorization}
    )
    return fig

@app.callback(
    Output("pie-chart", "figure"),
    [Input("categorization-dropdown", "value")]
)
def update_pie_chart(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    fig = px.pie(
        filtered_data,
        names=column,
        title="Vessel Distribution by Category",
    )
    return fig

@app.callback(
    Output("vessel-statistics-output", "children"),
    [Input("categorization-dropdown", "value")]
)
def update_vessel_statistics(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])

    stats = {
        "Total Vessels": len(filtered_data),
        "Vessels per Category": filtered_data[column].value_counts().to_dict(),
        "DWT Stats": filtered_data["Capacity - Dwt"].describe().to_dict(),
        "GT Stats": filtered_data["Capacity - Gt"].describe().to_dict(),
        "Length Stats": filtered_data["Length"].describe().to_dict(),
        "Draught Stats": filtered_data["Draught"].describe().to_dict(),
        "Average Speed Stats": filtered_data["Average Speed"].describe().to_dict(),
    }

    return html.Pre(str(stats))

# INSPECTOR PAGE

def database_inspector_page():
    return html.Div([
        html.H1("Database Inspector"),
        html.Div([
            dcc.Input(
                id="search-input",
                type="text",
                placeholder="Search...",
                style={"width": "300px", "margin-right": "10px"},
            ),
            dcc.Dropdown(
                id="column-filter-dropdown",
                options=[{"label": col, "value": col} for col in data.columns],
                multi=True,
                placeholder="Select columns to display",
                style={"width": "400px"},
            ),
        ], style={"margin-bottom": "20px"}),
        #dash.dash_table.DataTable(
        DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in data.columns],
            style_table={"overflowY": "auto", "maxHeight": "500px", "overflowX": "auto"},  # Enable vertical scrolling
            filter_action="native",  # Built-in filtering
            sort_action="native",    # Built-in sorting
            style_cell={"textAlign": "left"},  # Align text to the left for better readability
            style_data={"whiteSpace": "normal", "height": "auto"},  # Ensure rows adjust height for long text
        ),
        #dcc.Link("Go to Vessel Plots", href="/vessel-plots", style={"margin-right": "20px"}),
        #dcc.Link("Go to Vessel Statistics", href="/vessel-statistics"),
    ])

@app.callback(
    Output("data-table", "data"),
    [
        Input("search-input", "value"),
        Input("column-filter-dropdown", "value"),
    ]
)
def update_data_table(search_value, selected_columns):
    filtered_data = data.copy()

    # Apply column filtering
    if selected_columns:
        filtered_data = filtered_data[selected_columns]

    # Apply search filter
    if search_value:
        filtered_data = filtered_data[filtered_data.apply(
            lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1
        )]

    return filtered_data.to_dict("records")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@app.callback(
    Output("sfc-histogram", "figure"),
    Input("sfc-categorization-dropdown", "value")
)
def update_sfc_histogram(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = processed_data.copy()  # Use processed_data

    # Check if the selected column exists
    if column not in filtered_data.columns:
        return px.histogram(
            x=[],
            title=f"Error: '{column}' not found in the data",
            labels={"Fuel Consumption": "Fuel Consumption (tonnes/year)"}
        )

    # Apply flag categorization if needed
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])

    # Create the histogram
    fig = px.histogram(
        filtered_data,
        x="Fuel Consumption",
        color=column,
        title=f"Histogram of Fuel Consumption ({categorization})",
        labels={"Fuel Consumption": "Fuel Consumption (tonnes/year)"}
    )
    return fig


@app.callback(
    [Output("fuel-allocation-pie-chart", "figure"),
     Output("allocation-warning", "children")],
    [Input("hfo-input", "value"),
     Input("lfo-input", "value"),
     Input("mdo/mgo-input", "value"),
     Input("lng-input", "value")]
)
def update_fuel_allocation(hfo=52, lfo=31, mdo_mgo=12, lng=5):
    # Set defaults for missing inputs
    hfo = hfo if hfo is not None else 52
    lfo = lfo if lfo is not None else 31
    mdo_mgo = mdo_mgo if mdo_mgo is not None else 12
    lng = lng if lng is not None else 5

    total_allocation = hfo + lfo + mdo_mgo + lng
    if total_allocation != 100:
        return {}, f"Total allocation must equal 100%. Current total: {total_allocation}%"
    
    # Create pie chart
    fig = px.pie(
        values=[hfo, lfo, mdo_mgo, lng],
        names=["HFO", "LFO", "MDO/MGO", "LNG"],
        title="Fuel Type Allocation (%)"
    )
    return fig, ""

#FUEL CONSUMPTION CALLBACK
@app.callback(
    Output("total-fuel-consumption", "children"),
    [Input("sfc-categorization-dropdown", "value"),
     Input("hfo-input", "value"),
     Input("lfo-input", "value"),
     Input("mdo/mgo-input", "value"),
     Input("lng-input", "value")]
)
def calculate_total_fuel_consumption(categorization, hfo, lfo, mdo_mgo, lng):
    filtered_data = processed_data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    
    # Calculate total fuel consumption (tonnes)
    total_fuel = filtered_data["Fuel Consumption"].sum()

    # Validate that the allocation percentages sum to 100
    if hfo + lfo + mdo_mgo + lng != 100:
        return "Error: Fuel type allocation percentages must sum to 100%."

    # Energy content of fuels (in MJ/kg) CHECK IMO DATABASE TO SEE WHAT THEY ASSUME
    energy_content = {
        "HFO": 40.2,
        "LFO": 42.7,
        "MDO/MGO": 43.0,
        "LNG": 50.0,
    }

    # Calculate energy contributions (in TJ)
    energy_hfo = total_fuel * (hfo / 100) * energy_content["HFO"] / 1000
    energy_lfo = total_fuel * (lfo / 100) * energy_content["LFO"] / 1000
    energy_mdo_mgo = total_fuel * (mdo_mgo / 100) * energy_content["MDO/MGO"] / 1000
    energy_lng = total_fuel * (lng / 100) * energy_content["LNG"] / 1000

    total_energy = energy_hfo + energy_lfo + energy_mdo_mgo + energy_lng

    return (
        f"Total Fuel Consumption: {total_fuel:,.2f} tonnes\n"
        f"Total Energy: {total_energy:,.2f} TJ\n"
        f"(HFO: {energy_hfo:,.2f} TJ, LFO: {energy_lfo:,.2f} TJ, "
        f"MDO/MGO: {energy_mdo_mgo:,.2f} TJ, LNG: {energy_lng:,.2f} TJ)"
    )

#END OF FUEL CONSUMPTION CALLBACK
@app.callback(
    Output("fuel-consumption-category-table", "data"),
    Input("sfc-categorization-dropdown", "value")
)
def update_fuel_consumption_category_table(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = processed_data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    
    # Group by the selected category and sum fuel consumption
    category_summary = filtered_data.groupby(column)["Fuel Consumption"].sum().reset_index()
    category_summary.columns = [categorization, "Fuel Consumption (tonnes)"]
    return category_summary.to_dict("records")

@app.callback(
    Output("fuel-consumption-category-bar-chart", "figure"),
    [
        Input("sfc-categorization-dropdown", "value"),
        Input("hfo-input", "value"),
        Input("lfo-input", "value"),
        Input("mdo/mgo-input", "value"),
        Input("lng-input", "value"),
    ]
)
def update_fuel_consumption_category_bar_chart(categorization, hfo, lfo, mdo_mgo, lng):
    # Validate inputs
    hfo = hfo or 70
    lfo = lfo or 10
    mdo_mgo = mdo_mgo or 10
    lng = lng or 10

    total_allocation = hfo + lfo + mdo_mgo + lng
    if total_allocation != 100:
        return px.bar(
            x=[],
            y=[],
            title=f"Error: Total allocation must equal 100%. Current total: {total_allocation}%",
            labels={"x": "Category", "y": "Fuel Consumption (TJ)"},
        )

    # Filter data based on the categorization
    column = get_column_from_categorization(categorization)
    filtered_data = processed_data.copy()

    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])

    # Group by the selected category and calculate total fuel consumption
    category_summary = filtered_data.groupby(column)["Fuel Consumption"].sum().reset_index()

    # Energy content of fuels (in MJ/kg)
    energy_content = {
        "HFO": 40.2,
        "LFO": 42.7,
        "MDO/MGO": 43.0,
        "LNG": 50.0,
    }

    # Create fuel consumption breakdown for each category
    fuel_data = []
    for _, row in category_summary.iterrows():
        category = row[column]
        total_fuel = row["Fuel Consumption"]
        fuel_data.append({
            "Category": category,
            "Fuel Type": "HFO",
            "Fuel Consumption (TJ)": total_fuel * (hfo / 100) * energy_content["HFO"] / 1000,
        })
        fuel_data.append({
            "Category": category,
            "Fuel Type": "LFO",
            "Fuel Consumption (TJ)": total_fuel * (lfo / 100) * energy_content["LFO"] / 1000,
        })
        fuel_data.append({
            "Category": category,
            "Fuel Type": "MDO/MGO",
            "Fuel Consumption (TJ)": total_fuel * (mdo_mgo / 100) * energy_content["MDO/MGO"] / 1000,
        })
        fuel_data.append({
            "Category": category,
            "Fuel Type": "LNG",
            "Fuel Consumption (TJ)": total_fuel * (lng / 100) * energy_content["LNG"] / 1000,
        })

    # Convert to DataFrame for plotting
    fuel_df = pd.DataFrame(fuel_data)

    # Create stacked bar chart
    fig = px.bar(
        fuel_df,
        x="Category",
        y="Fuel Consumption (TJ)",
        color="Fuel Type",
        title="Fuel Consumption (TJ) by Category and Fuel Type",
        labels={"Category": categorization, "Fuel Consumption (TJ)": "Fuel Consumption (TJ)"},
    )

    return fig


@app.callback(
    [Output("fuel-consumption-bar-chart", "figure"),
    Output("fuel-consumption-data", "data")], #added to add data stired
    [
        Input("sfc-categorization-dropdown", "value"),
        Input("hfo-input", "value"),
        Input("lfo-input", "value"),
        Input("mdo/mgo-input", "value"),
        Input("lng-input", "value"),
    ]
)
def update_fuel_consumption_bar_chart(categorization, hfo, lfo, mdo_mgo, lng):
    # Validate inputs
    hfo = hfo or 70
    lfo = lfo or 10
    mdo_mgo = mdo_mgo or 10
    lng = lng or 10

    total_allocation = hfo + lfo + mdo_mgo + lng
    if total_allocation != 100:
        return px.bar(
            x=[],
            y=[],
            title=f"Error: Total allocation must equal 100%. Current total: {total_allocation}%",
            labels={"x": "Fuel Type", "y": "Energy Consumption (TJ)"},
        )
        return empty_fig, {} #ADDED BUT MAYBE UNNECESSARY

    # Filter data based on the categorization
    column = get_column_from_categorization(categorization)
    filtered_data = processed_data.copy()

    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])

    # Calculate total fuel consumption
    total_fuel = filtered_data["Fuel Consumption"].sum()

    # Energy content of fuels (in MJ/kg)
    energy_content = {
        "HFO": 40.2,
        "LFO": 42.7,
        "MDO/MGO": 43.0,
        "LNG": 50.0,
    }

    # Calculate energy consumption for each fuel type (convert MJ to TJ)
    energy_values = {
        "HFO": total_fuel * (hfo / 100) * energy_content["HFO"] / 1000,
        "LFO": total_fuel * (lfo / 100) * energy_content["LFO"] / 1000,
        "MDO/MGO": total_fuel * (mdo_mgo / 100) * energy_content["MDO/MGO"] / 1000,
        "LNG": total_fuel * (lng / 100) * energy_content["LNG"] / 1000,
    }
    print("Energy Values (TJ):", energy_values) #DEBUGGING
    # Create a bar chart
    fig = px.bar(
        x=list(energy_values.keys()),
        y=list(energy_values.values()),
        labels={"x": "Fuel Type", "y": "Energy Consumption (TJ)"},
        title="Total Fuel Consumption (TJ) by Fuel Type",
    )

    return fig, energy_values





@app.callback(
    Output("sfc-summary-table", "data"),
    Input("sfc-categorization-dropdown", "value")
)
def update_sfc_summary_table(categorization):
    filtered_data = data.copy()  # Use original data for missing value counts

    # Treat 0 values as missing
    summary = {
        "Metric": [
            "Ships with DWT, Speed, Days",
            "Ships Missing Speed",
            "Ships Missing Days",
            "Ships Missing DWT",
            "Ships Missing DWT and Draught",
            "Ships Missing DWT and Length",
            "Ships Missing DWT and GT",
            "Ships Missing DWT, Length, and Draught",
            "Ships Missing DWT, GT, and Draught",
            "Ships Missing DWT, GT, and Length",
            "Ships Missing DWT, GT, Length, and Draught",
        ],
        "Count": [
            len(filtered_data.dropna(subset=["Capacity - Dwt", "Average Speed", "Operational Days"])),
            len(filtered_data[(filtered_data["Average Speed"].isna()) | (filtered_data["Average Speed"] == 0)]),
            len(filtered_data[(filtered_data["Operational Days"].isna()) | (filtered_data["Operational Days"] == 0)]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna()) | (filtered_data["Capacity - Dwt"] == 0)]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Draught"].isna() | (filtered_data["Draught"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Length"].isna() | (filtered_data["Length"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Capacity - Gt"].isna() | (filtered_data["Capacity - Gt"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Length"].isna() | (filtered_data["Length"] == 0)) & 
                              (filtered_data["Draught"].isna() | (filtered_data["Draught"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Capacity - Gt"].isna() | (filtered_data["Capacity - Gt"] == 0)) & 
                              (filtered_data["Draught"].isna() | (filtered_data["Draught"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Capacity - Gt"].isna() | (filtered_data["Capacity - Gt"] == 0)) & 
                              (filtered_data["Length"].isna() | (filtered_data["Length"] == 0))]),
            len(filtered_data[(filtered_data["Capacity - Dwt"].isna() | (filtered_data["Capacity - Dwt"] == 0)) & 
                              (filtered_data["Capacity - Gt"].isna() | (filtered_data["Capacity - Gt"] == 0)) & 
                              (filtered_data["Length"].isna() | (filtered_data["Length"] == 0)) & 
                              (filtered_data["Draught"].isna() | (filtered_data["Draught"] == 0))]),
        ],
    }
    return pd.DataFrame(summary).to_dict("records")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# SCENARIO MODELLING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#pagelayout
def decarbonisation_scenarios_page():
    return html.Div([
        html.H1("Decarbonisation Scenarios"),
        html.Div([
            html.H3("General Assumptions"),
            html.Label("Annual Growth Rate (%):"),
            dcc.Input(id="annual-growth-rate", type="number", value=2, step=0.1),
            html.Label("Target Year:"),
            dcc.Input(id="end-year", type="number", value=2050, step=1),
        ]),
        html.Div([
            html.H3("Conversion to Clean Fuel"),
            html.Label("MDO/MGO Split (%):"),
            dcc.Input(id="mdo-mgo-split", type="number", value=50, step=1),
            html.Label("Annual MDO to MGO Conversion Rate (%):"),
            dcc.Input(id="mdo-to-mgo-rate", type="number", value=2, step=0.1),
            html.Label("Annual HFO to LFO Conversion Rate (%):"),
            dcc.Input(id="hfo-to-lfo-rate", type="number", value=3, step=0.1),
            html.Label("General Clean Fuel Conversion Rate (%):"),
            dcc.Input(id="clean-fuel-rate", type="number", value=5, step=0.1),
        ]),
        html.Div([
            html.H3("Prioritisation and Moderation"),
            html.Label("Phase-Out Prioritisation Vector (HFO, LFO, MDO, MGO, LNG):"),
            dcc.Input(id="prioritisation-vector", type="text", value="10,8,6,4,2"),
            html.Label("Moderation Factors (HFO, LFO, MDO, MGO, LNG):"),
            dcc.Input(id="moderation-factors", type="text", value="1,1,1,1,1"),
            html.H4("Phase-Out Prioritisation Matrix"),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th("Fossil Fuel / Clean Fuel")] + 
                                       [html.Th(fuel) for fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]])),
                    html.Tbody([
                        html.Tr([html.Th("HFO")] + [dcc.Input(id=f"matrix-hfo-{clean_fuel.lower().replace(' ', '-')}", type="number", value=10) for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]]),
                        html.Tr([html.Th("LFO")] + [dcc.Input(id=f"matrix-lfo-{clean_fuel.lower().replace(' ', '-')}", type="number", value=8) for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]]),
                        html.Tr([html.Th("MDO")] + [dcc.Input(id=f"matrix-mdo-{clean_fuel.lower().replace(' ', '-')}", type="number", value=6) for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]]),
                        html.Tr([html.Th("MGO")] + [dcc.Input(id=f"matrix-mgo-{clean_fuel.lower().replace(' ', '-')}", type="number", value=4) for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]]),
                        html.Tr([html.Th("LNG")] + [dcc.Input(id=f"matrix-lng-{clean_fuel.lower().replace(' ', '-')}", type="number", value=2) for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]]),
                    ]),
                ])
            ]),
        ]),
        html.Div([
            html.Button("Start Calculation", id="start-calculation-button", n_clicks=0),
            html.Button("Abort Calculation", id="abort-calculation-button", n_clicks=0, style={"margin-left": "10px"}),
        ]),
        html.Div([
            html.Label("Calculation Progress:"),
            html.Progress(id="decarbonisation-progress", value="0", max="100", style={"width": "100%"}),
        ], style={"margin-top": "20px"}),
        html.Div(id="decarbonisation-output"),
    ])


#model

# Global variable to manage calculation state
is_calculating = False
@app.callback(
    [
        Output("decarbonisation-progress", "value"),
        Output("decarbonisation-progress", "max"),
        Output("decarbonisation-output", "children"),
    ],
    [
        Input("start-calculation-button", "n_clicks"),
        Input("abort-calculation-button", "n_clicks"),
    ],
    [
        State("annual-growth-rate", "value"),
        State("end-year", "value"),
        State("mdo-mgo-split", "value"),
        State("mdo-to-mgo-rate", "value"),
        State("hfo-to-lfo-rate", "value"),
        State("clean-fuel-rate", "value"),
        State("prioritisation-vector", "value"),
        State("moderation-factors", "value"),
        *[State(f"matrix-{fossil_fuel.lower()}-{clean_fuel.lower().replace(' ', '-')}", "value")
          for fossil_fuel in ["hfo", "lfo", "mdo", "mgo", "lng"]
          for clean_fuel in ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]],
    ],
)
def calculate_decarbonisation_scenarios(
    start_clicks,
    abort_clicks,
    annual_growth_rate,
    end_year,
    mdo_mgo_split,
    mdo_to_mgo_rate,
    hfo_to_lfo_rate,
    clean_fuel_rate,
    prioritisation_vector,
    moderation_factors,
    *matrix_values,
):
    global is_calculating

    # Convert string inputs to floats
    try:
        annual_growth_rate = float(annual_growth_rate)
        end_year = int(end_year)
        mdo_mgo_split = float(mdo_mgo_split)
        mdo_to_mgo_rate = float(mdo_to_mgo_rate)
        hfo_to_lfo_rate = float(hfo_to_lfo_rate)
        clean_fuel_rate = float(clean_fuel_rate)
        prioritisation_vector = [float(x) for x in prioritisation_vector.split(",")]
        moderation_factors = [float(x) for x in moderation_factors.split(",")]
    except ValueError as e:
        print(f"Error converting inputs: {e}")
        return 0, 100, "Invalid input values."

    # Convert matrix_values into a prioritisation matrix
    try:
        prioritisation_matrix = [
            [float(value) for value in matrix_values[i:i + 5]]
            for i in range(0, len(matrix_values), 5)
        ]
    except ValueError as e:
        print(f"Error converting prioritisation matrix: {e}")
        return 0, 100, "Invalid prioritisation matrix values."

    # Validate prioritisation matrix dimensions
    if len(prioritisation_matrix) != 5 or any(len(row) != 5 for row in prioritisation_matrix):
        print("Invalid prioritisation matrix dimensions.")
        return 0, 100, "Invalid prioritisation matrix dimensions."

    # Determine the triggered button
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "abort-calculation-button" and is_calculating:
        is_calculating = False
        return 0, 100, "Calculation aborted."

    if triggered_id != "start-calculation-button" or is_calculating:
        raise PreventUpdate

    is_calculating = True

    # Manually initialize energy values
    energy_values = {
        "HFO": 23038.72640366435,
        "LFO": 14588.768723943025,
        "MDO/MGO": 5686.941649584196,
        "LNG": 2755.3011868140484,
    }

    # Split "MDO/MGO" into "MDO" and "MGO"
    mdo_percentage = mdo_mgo_split / 100
    mgo_percentage = 1 - mdo_percentage
    energy_values["MDO"] = energy_values["MDO/MGO"] * mdo_percentage
    energy_values["MGO"] = energy_values["MDO/MGO"] * mgo_percentage
    del energy_values["MDO/MGO"]

    # Add clean fuels
    clean_fuels = ["Green Hydrogen", "Biofuels", "Ammonia", "Electricity", "Methanol"]
    for clean_fuel in clean_fuels:
        energy_values[clean_fuel] = 0.0

    # Debugging: Print initialized energy values
    print("Initialized Energy Values (TJ):", energy_values)

    # Initialize results
    start_year = 2025
    years = list(range(start_year, end_year + 1))
    results = {year: {fuel: 0 for fuel in energy_values.keys()} for year in years}
    results[start_year] = energy_values.copy()

    # Normalize prioritisation vector
    total_priority = sum(prioritisation_vector)
    prioritisation_vector = [p / total_priority for p in prioritisation_vector]

    # Perform calculations
    progress_value = 0
    for year in years[1:]:
        if not is_calculating:
            break

        growth_factor = (1 + annual_growth_rate / 100) ** (year - start_year)
        for fuel, value in results[year - 1].items():
            results[year][fuel] = value * growth_factor

        # Apply MDO to MGO conversion
        results[year]["MGO"] += results[year]["MDO"] * (mdo_to_mgo_rate / 100)
        results[year]["MDO"] -= results[year]["MDO"] * (mdo_to_mgo_rate / 100)

        # Apply HFO to LFO conversion
        results[year]["LFO"] += results[year]["HFO"] * (hfo_to_lfo_rate / 100)
        results[year]["HFO"] -= results[year]["HFO"] * (hfo_to_lfo_rate / 100)

        # General clean fuel conversion
        for fossil_fuel in results[year]:
            if fossil_fuel in ["HFO", "LFO", "MDO", "MGO", "LNG"]:
                phase_out_amount = results[year][fossil_fuel] * (clean_fuel_rate / 100)
                weights = prioritisation_matrix[
                    list(energy_values.keys()).index(fossil_fuel)
                ]
                weight_sum = sum(weights)
                if weight_sum > 0:
                    for idx, clean_fuel in enumerate(clean_fuels):
                        proportion = weights[idx] / weight_sum
                        results[year][clean_fuel] += phase_out_amount * proportion
                        results[year][fossil_fuel] -= phase_out_amount * proportion

        # Update progress
        progress_value += 1

    is_calculating = False

    # Prepare results graph
    df_results = pd.DataFrame.from_dict(results, orient="index").reset_index()
    df_results.rename(columns={"index": "Year"}, inplace=True)


    fig = px.area(
    df_results,
    x="Year",
    y=list(df_results.columns[1:]),
    title="Decarbonisation Scenarios: Energy Consumption by Year",
    labels={"value": "Energy (TJ)", "variable": "Fuel Type"},
)
    # Customize the area chart appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Energy Consumption (TJ)",
        legend_title="Fuel Type",
        template="plotly_white",
)

    # Calculate the fuel percentages for the target year
    final_year_data = results[end_year]
    clean_fuel_data = {fuel: value for fuel, value in final_year_data.items() if fuel in clean_fuels}

# Calculate the total energy consumption for clean fuels
    clean_fuel_total = sum(clean_fuel_data.values())
    clean_fuel_percentages = {
        fuel: (value / clean_fuel_total) * 100 if clean_fuel_total > 0 else 0
        for fuel, value in clean_fuel_data.items()
}

# Create a pie chart for clean fuel percentages
    pie_fig = px.pie(
        names=list(clean_fuel_percentages.keys()),
        values=list(clean_fuel_percentages.values()),
        title=f"Clean Fuels Percentage in {end_year}",
        labels={"value": "Percentage", "names": "Clean Fuel"},
)

# Customize the pie chart appearance
    pie_fig.update_layout(
        legend_title="Clean Fuels",
        template="plotly_white",
)

    # Calculate the clean and fossil fuel percentages for the target year
    final_year_data = results[end_year]
    clean_fuel_data = {fuel: value for fuel, value in final_year_data.items() if fuel in clean_fuels}
    fossil_fuel_data = {fuel: value for fuel, value in final_year_data.items() if fuel not in clean_fuels}

    clean_fuel_total = sum(clean_fuel_data.values())
    fossil_fuel_total = sum(fossil_fuel_data.values())
    total_energy = clean_fuel_total + fossil_fuel_total

    # Create the clean vs fossil fuels pie chart
    fuel_type_percentages = {
        "Clean Fuels": (clean_fuel_total / total_energy) * 100 if total_energy > 0 else 0,
        "Fossil Fuels": (fossil_fuel_total / total_energy) * 100 if total_energy > 0 else 0,
    }

    clean_vs_fossil_pie = px.pie(
        names=list(fuel_type_percentages.keys()),
        values=list(fuel_type_percentages.values()),
        title=f"Clean vs Fossil Fuels in {end_year}",
        labels={"value": "Percentage", "names": "Fuel Type"},
    )
    clean_vs_fossil_pie.update_layout(
        legend_title="Fuel Types",
        template="plotly_white",
    )

    # Prepare the clean fuels percentage pie chart
    clean_fuel_percentages = {
        fuel: (value / clean_fuel_total) * 100 if clean_fuel_total > 0 else 0
        for fuel, value in clean_fuel_data.items()
    }

    clean_fuel_pie = px.pie(
        names=list(clean_fuel_percentages.keys()),
        values=list(clean_fuel_percentages.values()),
        title=f"Clean Fuels Percentage in {end_year}",
        labels={"value": "Percentage", "names": "Clean Fuel"},
    )
    clean_fuel_pie.update_layout(
        legend_title="Clean Fuels",
        template="plotly_white",
    )


    return str(progress_value), str(len(years)), html.Div([dcc.Graph(figure=fig),dcc.Graph(figure=pie_fig),dcc.Graph(figure=clean_vs_fossil_pie),]),



# FINAL PAGE DEFINITIONS

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/vessel-statistics":
        return vessel_statistics_page()
    elif pathname == "/vessel-plots":
        return vessel_plots_page()
    elif pathname == "/database-inspector":
        return database_inspector_page()
    elif pathname == "/sfc-analysis":
        return sfc_analysis_page()
    elif pathname == "/decarbonisation-scenarios":
        return decarbonisation_scenarios_page()  # Add the new page here
    return vessel_plots_page()  # Default to Vessel Plots

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)