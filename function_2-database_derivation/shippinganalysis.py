import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
from dash.dash_table import DataTable
from sklearn.linear_model import LinearRegression # Helper functions for regression-based DWT estimation
import numpy as np
import dash
import time
from dash.exceptions import PreventUpdate
from dash import dash_table

import plotly.express as px
import plotly.colors as pc
from plotly.subplots import make_subplots

# Extended color palette (40+ unique colors)
extended_colors = (
    pc.qualitative.Alphabet +
    pc.qualitative.Set3 +
    pc.qualitative.Dark24 +
    pc.qualitative.Light24 +
    pc.qualitative.Pastel1
)

# Database Details - specify here
excel_file = "complete_database_foranalysis.xlsx" #"finaloutput.xlsx" #this was the one used to get histogram final for DWT since it was complete #"outputtrue.xlsx"this was the old one
sheet_name = "Sheet1"
columns_to_import = ["Flag",
                     "Vessel Name", 
                     "Imo",
                     "Capacity - Dwt", 
                     "Capacity - Gt", 
                     "Length", 
                     "Draught",
                     "Built",
                     "Average Speed",
                     "Vessel Type - Generic",
                     "Vessel Type - Detailed",
                     "Fuel Consumption",
                     "Fuel Type",
                     "Energy Consumption (TJ/year)"
                     ]

# --- ADD THIS ---
empirical_file = "outputtrue.xlsx"
empirical = pd.read_excel(empirical_file, sheet_name=sheet_name, usecols=columns_to_import)



# Read the data from the Excel file
data = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=columns_to_import)

# Add Operational Days to both datasets (((((BECAUSE FOR NOW WE DON?T HAVE THESE!)))))
data["Operational Days"] = 0.8 * 365  # Default operational days

# Fill missing average speed with the dataset-wide average ((MIGHT NEED TO CHANGE THIS TO API))
data["Average Speed"] = data["Average Speed"].fillna(data["Average Speed"].mean())

# Replace NaN values with 0 for the entire DataFrame
columns_to_fill = ["Capacity - Dwt", "Capacity - Gt", "Length", "Draught"]
data[columns_to_fill] = data[columns_to_fill].fillna(0)

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
    "High Speed Craft": "Specialized Vessels", #added
    "Other": "Specialized Vessels",
    "": "Specialized Vessels",
}

data["Vessel Type - Simplified"] = data["Vessel Type - Detailed"].map(simplified_mapping)

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
    "High Speed Craft": "Rest", #added
    "Other": "Rest",
    "": "Rest",
}

data["Vessel Type - Contextual"] = data["Vessel Type - Detailed"].map(contextual_categories)

# (Optional but recommended: keep schema aligned for filtering/colouring)
empirical["Vessel Type - Simplified"] = empirical["Vessel Type - Detailed"].map(simplified_mapping)
empirical["Vessel Type - Contextual"] = empirical["Vessel Type - Detailed"].map(contextual_categories)


# Apply the updated dwt estimation - for now just based on average of that type :(
def estimate_dwt_by_average(data):
    # Step 1: Calculate average DWT by Vessel Type - Detailed and Vessel Type - Contextual
    avg_dwt_detailed = (
        data[data["Capacity - Dwt"] > 0]
        .groupby("Vessel Type - Detailed")["Capacity - Dwt"]
        .mean()
        .to_dict()
    )

    avg_dwt_contextual = (
        data[data["Capacity - Dwt"] > 0]
        .groupby("Vessel Type - Contextual")["Capacity - Dwt"]
        .mean()
        .to_dict()
    )

    # Step 2: Fill DWT values with the averages
    def fill_dwt(row):
        if row["Capacity - Dwt"] > 0:  # If DWT is already non-zero, keep it
            return row["Capacity - Dwt"]
        # Try Vessel Type - Detailed average first
        if row["Vessel Type - Detailed"] in avg_dwt_detailed:
            return avg_dwt_detailed[row["Vessel Type - Detailed"]]
        # Fallback to Vessel Type - Contextual average
        if row["Vessel Type - Contextual"] in avg_dwt_contextual:
            return avg_dwt_contextual[row["Vessel Type - Contextual"]]
        # Default to 0 if no match is found
        return 0

    # Apply the logic to estimate DWT
    data["Estimated DWT"] = data.apply(fill_dwt, axis=1)
    return data

data = estimate_dwt_by_average(data)

# Calculate ship fuel consumption
def calculate_fuel_consumption(row):
    """Calculate fuel consumption for a given ship."""
    dwt = max(row["Estimated DWT"], 0)  # Ensure non-negative DWT
    avg_speed = max(row["Average Speed"], 0)  # Ensure non-negative speed
    operational_days = max(row["Operational Days"], 0)  # Ensure non-negative operational days
    return (1 / 120000) * (dwt**(2 / 3)) * (avg_speed**3) * operational_days

data["Fuel Consumption"] = data.apply(calculate_fuel_consumption, axis=1)

# zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz

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

# Emission intensities of fuels (per emission type)
EMISSION_INTENSITIES = {
    "HFO": {"CO2": 77.4, "SOx": 1.5, "NOx": 3.2, "PM": 0.1},
    "LFO": {"CO2": 74.0, "SOx": 0.8, "NOx": 2.8, "PM": 0.05},
    "MDO": {"CO2": 73.5, "SOx": 0.6, "NOx": 2.5, "PM": 0.04},
    "MGO": {"CO2": 73.5, "SOx": 0.6, "NOx": 2.5, "PM": 0.04},
    "LNG": {"CO2": 56.1, "SOx": 0.0, "NOx": 1.7, "PM": 0.01},
    "Hydrogen": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.0, "PM": 0.0},
    "Biofuels": {"CO2": 10.0, "SOx": 0.2, "NOx": 1.0, "PM": 0.02},
    "Ammonia": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.5, "PM": 0.0},
    "Electricity": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.0, "PM": 0.0},
    "Methanol": {"CO2": 22.0, "SOx": 0.1, "NOx": 1.2, "PM": 0.03},
}

# Energy content of fuels (in MJ/kg)
energy_content = {
    "HFO": 40.2,
    "LFO": 42.7,
    "MDO": 43.0,
    "MGO": 43.0,
    "LNG": 50.0,
}

# Determine which vessel types consume what type of fuel - this is required to convert SFC into energy values
fuel_type_mapping = {
    "Yacht": "MGO",
    "General Cargo": "HFO",
    "Research/Survey Vessel": "MGO",
    "Supply Vessel": "MGO",
    "Cable Layer": "MGO",
    "Military Ops": "MGO",
    "Special Craft": "MGO",
    "Ro-Ro/Vehicles Carrier": "HFO",
    "Container Ship": "HFO",
    "Fishing Vessel": "MDO", #MGO
    "Sailing Vessel": "None",  # Primarily wind-powered
    "Trawler": "MDO", #MGO
    "Special Pleasure Craft": "MGO",
    "Special Cargo": "HFO",
    "Other Special Craft": "MGO",
    "Passenger Vessel": "LFO", #was LFO but changed to MDO
    "Crude Oil Tanker": "HFO",
    "Oil/Chemical Tanker": "HFO",
    "LNG Tanker": "LNG",
    "Special Passenger Vessel": "MGO",
    "Anchor Handling Vessel": "MGO",
    "Barge": "MDO", #MGO
    "Reefer": "HFO",
    "Tug": "MGO",
    "LPG Tanker": "LNG",
    "Ro-Ro/Passenger Vessel": "LFO",
    "Bulk Carrier": "HFO",
    "Heavy Load Carrier": "HFO",
    "Oil Products Tanker": "HFO",
    "Platform": "MDO", #MGO
    "Passenger/Cargo Ship": "LFO",
    "Fish Carrier": "MGO",
    "Training Ship": "MGO",
    "Landing Craft": "MGO",
    "Fire Fighting Vessel": "MGO",
    "Offshore Vessel": "MGO",
    "Special Fishing Vessel": "MDO", #MGO
    "Other Pleasure Craft": "MGO",
    "Patrol Vessel": "MGO",
    "Search & Rescue": "MDO",#MGO
    "Other Passenger": "LFO",
    "Other Fishing": "MDO", #MGO
    "Other Cargo": "HFO",
    "Service Vessel": "MGO",
    "Pusher Tug": "MGO",
    "Unspecified": "MGO",
    "Pilot Boat": "MGO",
    "Navigation Aids": "MGO",
    "High Speed Craft": "MGO",
}

# Determine which fuel is consumed by which ship
data["Fuel Type"] = data["Vessel Type - Detailed"].map(fuel_type_mapping)

# Calculate Energy Consumption (TJ/year) and ensure it's a valid number
data["Energy Consumption (TJ/year)"] = (
    data["Fuel Consumption"] * data["Fuel Type"].map(energy_content).fillna(0) / 1000
)

# Handle potential complex values (ensure all values are real numbers)
data["Energy Consumption (TJ/year)"] = data["Energy Consumption (TJ/year)"].apply(
    lambda x: x.real if isinstance(x, complex) else x
)

output_file = "fuel_consumptions_per_vessel.xlsx"

    # Save the DataFrame to Excel
data.to_excel(output_file, index=False)

# Debugging checks commented out for now
#-----------------------------------------
#mdo_types = [key for key, value in fuel_type_mapping.items() if value == "MDO"]
#print(mdo_types)  # Should list all vessel types mapped to "MDO"
#print(data[data["Vessel Type - Detailed"].isin(mdo_types)])
#print(data["Energy Consumption (TJ/year)"].sum())


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# PAGES FOR EACH ASPECT OF THE TOOL

# App initialization with suppress_callback_exceptions=True
app = Dash(__name__, suppress_callback_exceptions=True)

# Helper functions for page layouts
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
#NEW ONES TEMPORARY
        html.Div([
            html.H3("Final Bar Chart"),
            dcc.Graph(id="static-bar-chart"),
        ]),
        html.Div([
            html.H3("Energy Final Bar Chart"),
            dcc.Graph(id="static-energy-bar-chart"),
        ]),
        html.Div([
            html.H3("Final Pie Chart"),
            dcc.Graph(id="static-pie-chart"),
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

def sfc_analysis_page():
    return html.Div([
        html.H1("SFC Analysis"),
        html.Div([
            html.H3("Histogram of Ship Energy Consumption"),
            dcc.Dropdown(
                id="sfc-categorization-dropdown",
                options=[
                {"label": "Fuel Type", "value": "Fuel Type"},
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
                value="Fuel Type",  # Default categorization by fuel type
                clearable=False,
            ),
            dcc.Graph(id="sfc-energy-histogram"),
            dcc.Graph(id="sfc-energy-pie-chart"),
            dcc.Graph(id="sfc-energy-bar-chart"),
            dcc.Graph(id="sfc-fuel-type-bar-chart"),
        ]),
        
    ])

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
            html.H3("Efficiency Measures"),
            html.H4("Hull Coating & Propeller Polishing"),
            html.Label("Adoption Rate (%):"),
            dcc.Input(id="hull-coating-adoption-rate", type="number", value=10, step=0.1),
            html.Label("Efficiency Savings (%):"),
            dcc.Input(id="hull-coating-savings", type="number", value=5, step=0.1),
            html.H4("Slow Steaming"),
            html.Label("Adoption Rate (%):"),
            dcc.Input(id="slow-steaming-adoption-rate", type="number", value=10, step=0.1),
            html.Label("Efficiency Savings (%):"),
            dcc.Input(id="slow-steaming-savings", type="number", value=5, step=0.1),
            html.H4("Sailing & Hybrid"),
            html.Label("Adoption Rate (%):"),
            dcc.Input(id="sailing-hybrid-adoption-rate", type="number", value=5, step=0.1),
            html.Label("Efficiency Savings (%):"),
            dcc.Input(id="sailing-hybrid-savings", type="number", value=10, step=0.1),
        ]),
        html.Div([
            html.H3("Clean Fuel Transition"),
            html.Label("Annual Clean Fuel Adoption Rate (%):"),
            dcc.Input(id="clean-fuel-rate", type="number", value=5, step=0.1),
        ]),
        html.Div([
            html.Button("Start Calculation", id="start-calculation-button", n_clicks=0),
            html.Button("Abort Calculation", id="abort-calculation-button", n_clicks=0, style={"margin-left": "10px"}),
        ], style={"margin-top": "20px"}),
        html.Div([
            html.Label("Calculation Progress:"),
            html.Progress(id="decarbonisation-progress", value="0", max="100", style={"width": "100%"}),
        ], style={"margin-top": "20px"}),
        html.Div(id="decarbonisation-output"),
    ])


# LAYOUT FOR TOOL ----------------NAVIGATION BAR-----------------------
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
#----------------------------------------------------------------------
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# FUNCTIONS OF EACH PAGE

# (1) PLOTS PLAGE
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

from plotly.subplots import make_subplots

@app.callback(
    Output("histogram", "figure"),
    [
        Input("categorization-dropdown", "value"),
        Input("histogram-variable-dropdown", "value"),
    ]
)
def update_histogram(categorization, variable):
    column = get_column_from_categorization(categorization)

    # --- TOP: combined (finaloutput.xlsx) ---
    filtered_data = data.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])
    filtered_data = filtered_data[filtered_data[variable].notnull() & (filtered_data[variable] > 0)]

    # --- BOTTOM: empirical-only (outputtrue.xlsx) ---
    empirical_filtered = empirical.copy()
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        empirical_filtered["Flag"] = empirical_filtered["Flag"].apply(lambda x: categorize_flag(x, categorization))
        empirical_filtered = empirical_filtered.dropna(subset=["Flag"])
    empirical_filtered = empirical_filtered[empirical_filtered[variable].notnull() & (empirical_filtered[variable] > 0)]

    # Base histogram (top; colored by category)
    fig = px.histogram(
        filtered_data,
        x=variable,
        color=column,
        title=f"Histogram: {variable} ({categorization})",
        nbins=100,
        color_discrete_sequence=extended_colors
    )

    # --- Mirror the empirical as a line below the x-axis ---
    import numpy as np
    import plotly.graph_objects as go

    if not (filtered_data.empty and empirical_filtered.empty):
        # Use the UNION of ranges so both datasets are fully covered
        xmin = float(min(
            filtered_data[variable].min() if not filtered_data.empty else np.inf,
            empirical_filtered[variable].min() if not empirical_filtered.empty else np.inf
        ))
        xmax = float(max(
            filtered_data[variable].max() if not filtered_data.empty else -np.inf,
            empirical_filtered[variable].max() if not empirical_filtered.empty else -np.inf
        ))
        if not np.isfinite(xmin) or not np.isfinite(xmax) or xmin == xmax:
            xmin, xmax = 0.0, 1.0

        nbins = 100
        bin_edges = np.linspace(xmin, xmax, nbins + 1)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Counts for top (combined) and bottom (empirical)
        top_counts, _ = np.histogram(
            filtered_data[variable].values if not filtered_data.empty else np.array([]),
            bins=bin_edges
        )
        emp_counts, _ = np.histogram(
            empirical_filtered[variable].values if not empirical_filtered.empty else np.array([]),
            bins=bin_edges
        )

        # --- how much space to leave above/below the tallest bars ---
        TOP_PAD = 1.1    # 25% headroom above the tallest TOP bin
        BOTTOM_PAD = 1.1  # 40% headroom below the tallest BOTTOM bin
        EXTRA_TOP = 0       # optional absolute extra counts on top
        EXTRA_BOTTOM = 0    # optional absolute extra counts on bottom

        top_max = int(top_counts.max()) if top_counts.size else 1
        bot_max = int(emp_counts.max()) if emp_counts.size else 1

        upper = TOP_PAD * top_max + EXTRA_TOP
        lower = -(BOTTOM_PAD * bot_max + EXTRA_BOTTOM)

        fig.update_yaxes(range=[lower, upper], zeroline=True, zerolinewidth=2)

        # Mirror the empirical line
        fig.add_trace(
            go.Scatter(
                x=bin_centers,
                y=-emp_counts,  # NEGATIVE => drawn below the x-axis (mirrored)
                mode="lines",
                name="Empirical only (reported DWT) — mirrored",
                line=dict(width=2, color="black")
            )
        )

        # Make sure the x-binning of the top hist matches these bins
        for tr in fig.data:
            if getattr(tr, "type", None) == "histogram":
                tr.xbins = dict(start=xmin, end=xmax, size=(xmax - xmin) / nbins)

        # Symmetric y-range so nothing is cut off
        #y_max = max(int(top_counts.max()) if top_counts.size else 1,
                    #int(emp_counts.max()) if emp_counts.size else 1)
        #fig.update_yaxes(range=[-1.15 * y_max, 1.15 * y_max], zeroline=True, zerolinewidth=2)

    # Styling (kept from your original)
    fig.update_layout(
        template="simple_white",
        xaxis_title="Capacity – DWT (tonnes)" if variable == "Capacity - Dwt" else variable,
        yaxis_title="Number of vessels",
        title_font_size=18,
        font_size=14,
        bargap=0.1
    )
    fig.update_layout(
        title="Histogram: Capacity – Dwt by Vessel Type – Detailed" if variable == "Capacity - Dwt"
              else f"Histogram: {variable} by {column}",
        template="simple_white",
        bargap=0.1,
        font=dict(size=16, family="Arial"),
        title_font=dict(size=20),
        legend_title_text="Vessel Type – Detailed" if column == "Vessel Type - Detailed" else column,
        width=1400,
        height=800,
        legend=dict(orientation="v", x=1.02, y=1, bgcolor="rgba(255,255,255,0)", borderwidth=0)
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

vessel_order = [
    "Passenger Vessel", "General Cargo", "Special Craft", "Supply Vessel", "Passenger/Cargo Ship",
    "Container Ship", "Ro-Ro/Vehicles Carrier", "LNG Tanker", "Special Cargo", "Other Special Craft", "Oil/Chemical Tanker", 
    "Reefer", "Bulk Carrier", "LPG Tanker", "Ro-Ro/Passenger Vessel", "Crude Oil Tanker",
    "Oil Products Tanker", "Heavy Load Carrier", "Other Passenger", "Landing Craft", "Special Passenger Vessel",
    "Other Cargo", "High Speed Craft"
]


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
        color=column,
        category_orders={column: vessel_order},  # Ensures pie slices + legend are in desired order
        color_discrete_sequence=extended_colors
    )


    # Update layout to show full legend on the side
    fig.update_layout(
        template="simple_white",
        title_font_size=20,
        font=dict(size=16, family="Arial"),
        legend_title_text=column,
        width=1400,
        height=800,
        legend=dict(
            orientation="v",
            x=1.02,  # Pushes legend to the right
            y=1,
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0
        )
    )

    return fig

#NEW TEMPORARY

# --- Helpers ---------------------------------------------------------------

EXPECTED_FUEL_TOTALS = {
    "Passenger Vessel": 127305.3003,
    "General Cargo": 55297.88393,
    "Special Craft": 2284.543448,
    "Supply Vessel": 320.739291,
    "Passenger/Cargo Ship": 204.7591617,
    "Container Ship": 142912.969,
    "Ro-Ro/Vehicles Carrier": 86101.39101,
    "LNG Tanker": 40561.61698,
    "Special Cargo": 2509.400311,
    "Other Special Craft": 4149.960021,
    "Oil/Chemical Tanker": 60465.6532,
    "Reefer": 32768.44478,
    "Bulk Carrier": 67511.24279,
    "LPG Tanker": 1603.427034,
    "Ro-Ro/Passenger Vessel": 5703.958665,
    "Crude Oil Tanker": 2805.941217,
    "Oil Products Tanker": 12437.61467,
    "Heavy Load Carrier": 575.2107637,
    "Other Passenger": 44440.19788,
    "Landing Craft": 2842.606035,
    "Special Passenger Vessel": 2834.687926,
    "Other Cargo": 1088.652398,
    "High Speed Craft": 1629.909944,
}

def _prep_chart_df(categorization):
    df = data.copy()

    # Apply same categorization logic as elsewhere (if you use it)
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        df["Flag"] = df["Flag"].apply(lambda x: categorize_flag(x, categorization))
        df = df.dropna(subset=["Flag"])

    # Standardise labels and coerce numerics
    df["Vessel Type - Detailed"] = df["Vessel Type - Detailed"].astype(str).str.strip()
    for col in ["Fuel Consumption", "Energy Consumption (TJ/year)", "Operational Days"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # De-duplicate: one row per vessel (prefer the row with highest Operational Days)
    key = "Imo" if "Imo" in df.columns else "Vessel Name"
    if "Operational Days" in df.columns:
        df = df.sort_values("Operational Days", ascending=False).drop_duplicates(subset=[key], keep="first")
    else:
        df = df.drop_duplicates(subset=[key], keep="first")

    return df

def _build_color_map():
    # Stable colors for known types; others fall back to Plotly defaults
    return dict(zip(vessel_order, extended_colors))

def _diagnose_against_expected(grouped, metric, expected_dict):
    try:
        computed = grouped.set_index("Vessel Type - Detailed")[metric]
        expected = pd.Series(expected_dict, name="expected")
        # Align on union of indexes to reveal missing/extra categories
        comp = pd.concat([computed, expected], axis=1)
        comp["diff"] = comp[metric] - comp["expected"]
        # Print top absolute differences
        print("\n[Diag] Top diffs vs expected ({})".format(metric))
        print(comp.reindex(comp["diff"].abs().sort_values(ascending=False).index).head(15).to_string())
        # Totals
        print(f"[Diag] Total computed: {computed.sum():,.6f} | Total expected: {expected.sum():,.6f} | Δ = {(computed.sum() - expected.sum()):,.6f}")
    except Exception as e:
        print(f"[Diag] Could not run expectation check: {e}")

# --- Manual totals provided by user (Fuel) ---
manual_fuel_data = [
    {"Vessel Type - Detailed": "Passenger Vessel",           "Fuel Consumption (tonnes/year)": 127305.3003},
    {"Vessel Type - Detailed": "General Cargo",              "Fuel Consumption (tonnes/year)": 55297.88393},
    {"Vessel Type - Detailed": "Special Craft",              "Fuel Consumption (tonnes/year)": 2284.543448},
    {"Vessel Type - Detailed": "Supply Vessel",              "Fuel Consumption (tonnes/year)": 320.739291},
    {"Vessel Type - Detailed": "Passenger/Cargo Ship",       "Fuel Consumption (tonnes/year)": 204.7591617},
    {"Vessel Type - Detailed": "Container Ship",             "Fuel Consumption (tonnes/year)": 142912.969},
    {"Vessel Type - Detailed": "Ro-Ro/Vehicles Carrier",     "Fuel Consumption (tonnes/year)": 86101.39101},
    {"Vessel Type - Detailed": "LNG Tanker",                 "Fuel Consumption (tonnes/year)": 40561.61698},
    {"Vessel Type - Detailed": "Special Cargo",              "Fuel Consumption (tonnes/year)": 2509.400311},
    {"Vessel Type - Detailed": "Other Special Craft",        "Fuel Consumption (tonnes/year)": 4149.960021},
    {"Vessel Type - Detailed": "Oil/Chemical Tanker",        "Fuel Consumption (tonnes/year)": 60465.6532},
    {"Vessel Type - Detailed": "Reefer",                     "Fuel Consumption (tonnes/year)": 32768.44478},
    {"Vessel Type - Detailed": "Bulk Carrier",               "Fuel Consumption (tonnes/year)": 67511.24279},
    {"Vessel Type - Detailed": "LPG Tanker",                 "Fuel Consumption (tonnes/year)": 1603.427034},
    {"Vessel Type - Detailed": "Ro-Ro/Passenger Vessel",     "Fuel Consumption (tonnes/year)": 5703.958665},
    {"Vessel Type - Detailed": "Crude Oil Tanker",           "Fuel Consumption (tonnes/year)": 2805.941217},
    {"Vessel Type - Detailed": "Oil Products Tanker",        "Fuel Consumption (tonnes/year)": 12437.61467},
    {"Vessel Type - Detailed": "Heavy Load Carrier",         "Fuel Consumption (tonnes/year)": 575.2107637},
    {"Vessel Type - Detailed": "Other Passenger",            "Fuel Consumption (tonnes/year)": 44440.19788},
    {"Vessel Type - Detailed": "Landing Craft",              "Fuel Consumption (tonnes/year)": 2842.606035},
    {"Vessel Type - Detailed": "Special Passenger Vessel",   "Fuel Consumption (tonnes/year)": 2834.687926},
    {"Vessel Type - Detailed": "Other Cargo",                "Fuel Consumption (tonnes/year)": 1088.652398},
    {"Vessel Type - Detailed": "High Speed Craft",           "Fuel Consumption (tonnes/year)": 1629.909944},
]

# --- Manual totals provided by user (Energy) ---
manual_energy_data = [
    {"Vessel Type - Detailed": "Passenger Vessel",           "Energy Consumption (TJ/year)": 5168.595191},
    {"Vessel Type - Detailed": "General Cargo",              "Energy Consumption (TJ/year)": 2156.617473},
    {"Vessel Type - Detailed": "Special Craft",              "Energy Consumption (TJ/year)": 97.77845958},
    {"Vessel Type - Detailed": "Supply Vessel",              "Energy Consumption (TJ/year)": 13.72764166},
    {"Vessel Type - Detailed": "Passenger/Cargo Ship",       "Energy Consumption (TJ/year)": 8.313221965},
    {"Vessel Type - Detailed": "Container Ship",             "Energy Consumption (TJ/year)": 5573.605792},
    {"Vessel Type - Detailed": "Ro-Ro/Vehicles Carrier",     "Energy Consumption (TJ/year)": 3357.954249},
    {"Vessel Type - Detailed": "LNG Tanker",                 "Energy Consumption (TJ/year)": 1971.294585},
    {"Vessel Type - Detailed": "Special Cargo",              "Energy Consumption (TJ/year)": 97.86661211},
    {"Vessel Type - Detailed": "Other Special Craft",        "Energy Consumption (TJ/year)": 177.6182889},
    {"Vessel Type - Detailed": "Oil/Chemical Tanker",        "Energy Consumption (TJ/year)": 2358.160475},
    {"Vessel Type - Detailed": "Reefer",                     "Energy Consumption (TJ/year)": 1277.969347},
    {"Vessel Type - Detailed": "Bulk Carrier",               "Energy Consumption (TJ/year)": 2632.938469},
    {"Vessel Type - Detailed": "LPG Tanker",                 "Energy Consumption (TJ/year)": 77.92655386},
    {"Vessel Type - Detailed": "Ro-Ro/Passenger Vessel",     "Energy Consumption (TJ/year)": 231.5807218},
    {"Vessel Type - Detailed": "Crude Oil Tanker",           "Energy Consumption (TJ/year)": 109.4317074},
    {"Vessel Type - Detailed": "Oil Products Tanker",        "Energy Consumption (TJ/year)": 485.066972},
    {"Vessel Type - Detailed": "Heavy Load Carrier",         "Energy Consumption (TJ/year)": 22.43321979},
    {"Vessel Type - Detailed": "Other Passenger",            "Energy Consumption (TJ/year)": 1804.272034},
    {"Vessel Type - Detailed": "Landing Craft",              "Energy Consumption (TJ/year)": 121.6635383},
    {"Vessel Type - Detailed": "Special Passenger Vessel",   "Energy Consumption (TJ/year)": 121.3246432},
    {"Vessel Type - Detailed": "Other Cargo",                "Energy Consumption (TJ/year)": 42.45744354},
    {"Vessel Type - Detailed": "High Speed Craft",           "Energy Consumption (TJ/year)": 69.76014562},
]

# --- Build static DataFrames (clean + sort) ---
df_manual_fuel = pd.DataFrame(manual_fuel_data)
df_manual_energy = pd.DataFrame(manual_energy_data)

# Clean labels (robust to any stray whitespace)
df_manual_fuel["Vessel Type - Detailed"] = df_manual_fuel["Vessel Type - Detailed"].astype(str).str.strip()
df_manual_energy["Vessel Type - Detailed"] = df_manual_energy["Vessel Type - Detailed"].astype(str).str.strip()

# Sort descending by metric so bars appear largest → smallest
df_manual_fuel = df_manual_fuel.sort_values("Fuel Consumption (tonnes/year)", ascending=False)
df_manual_energy = df_manual_energy.sort_values("Energy Consumption (TJ/year)", ascending=False)

# Stable colors using your existing lists
color_map = dict(zip(vessel_order, extended_colors))  # vessel_order + extended_colors must exist


# --- Fuel chart (static from manual totals) ---
@app.callback(
    Output("static-bar-chart", "figure"),
    [Input("categorization-dropdown", "value")]
)
def update_static_bar_chart(_categoriztion_ignored):
    grouped = df_manual_fuel

    fig = px.bar(
        grouped,
        x="Vessel Type - Detailed",
        y="Fuel Consumption (tonnes/year)",
        color="Vessel Type - Detailed",
        title="Total Fuel Consumption by Vessel Type (tonnes/year)",
        color_discrete_map=color_map
    )

    fig.update_layout(
        template="simple_white",
        font=dict(size=14),
        title_font=dict(size=18),
        legend_title_text="Vessel Type",
        width=1400,
        height=800,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
            traceorder="normal",
            bgcolor="rgba(255,255,255,0)",
            bordercolor="Black",
            borderwidth=0
        )
    )
    return fig


# --- Energy chart (static from manual totals) ---
@app.callback(
    Output("static-energy-bar-chart", "figure"),
    [Input("categorization-dropdown", "value")]
)
def update_static_energy_bar_chart(_categoriztion_ignored):
    grouped = df_manual_energy

    fig = px.bar(
        grouped,
        x="Vessel Type - Detailed",
        y="Energy Consumption (TJ/year)",
        color="Vessel Type - Detailed",
        title="Total Energy Consumption by Vessel Type (TJ/year)",
        color_discrete_map=color_map
    )

    fig.update_layout(
        template="simple_white",
        font=dict(size=14),
        title_font=dict(size=18),
        legend_title_text="Vessel Type",
        width=1400,
        height=800,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
            traceorder="normal",
            bgcolor="rgba(255,255,255,0)",
            bordercolor="Black",
            borderwidth=0
        )
    )
    return fig





@app.callback(
    Output("static-pie-chart", "figure"),
    [Input("categorization-dropdown", "value")]
)
def update_static_pie_chart(categorization):
    # Hardcoded values
    grouped = pd.DataFrame({
        "Fuel Type": ["HFO", "LFO", "MGO", "LNG"],
        "Fuel Consumption": [236482.5, 84963.1, 25952.824, 37278.03]
    })

    # Calculate percentages and external labels
    total = grouped["Fuel Consumption"].sum()
    grouped["Percentage"] = (grouped["Fuel Consumption"] / total) * 100
    grouped["Label Inside"] = grouped["Percentage"].apply(lambda x: f"{x:.1f}%")
    grouped["Label Outside"] = grouped.apply(
        lambda row: f"{row['Fuel Type']}: {row['Fuel Consumption']:,.0f} t/y", axis=1
    )

    # Create pie chart
    fig = px.pie(
        grouped,
        names="Label Outside",  # outside label
        values="Fuel Consumption",
        hole=0.3
    )

    # Update the trace to show % only inside
    fig.update_traces(
        text=grouped["Label Inside"],
        textposition="inside",
        insidetextorientation="auto",
        hovertemplate='%{label}<br>%{value:,.0f} t/y<br>%{percent}'
    )

    fig.update_layout(
        title="Fuel Consumption by Fuel Type (tonnes/year)",
        template="simple_white",
        font=dict(size=14),
        title_font=dict(size=18),
        legend_title_text="Fuel Type",
        width=800,
        height=600
    )

    return fig

# (2) STATISTICS PAGE
@app.callback(
    Output("vessel-statistics-output", "children"),
    [Input("categorization-dropdown", "value")]
)
def update_vessel_statistics(categorization):
    column = get_column_from_categorization(categorization)
    filtered_data = data.copy()

    # Filter data based on categorization
    if categorization in ["Pacific - Simplified", "Pacific - Detailed", "Pacific Only", "Other Only"]:
        filtered_data["Flag"] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=["Flag"])

    # Calculate vessel length statistics
    vessels_greater_15m = filtered_data[filtered_data["Length"] > 15].shape[0]
    vessels_less_15m = filtered_data[(filtered_data["Length"] > 0) & (filtered_data["Length"] <= 15)].shape[0]
    vessels_missing_length = filtered_data[(filtered_data["Length"].isna()) | (filtered_data["Length"] <= 0)].shape[0]

    # Generate overall statistics
    stats = {
        "Total Vessels": len(filtered_data),
        "Vessels >15m": vessels_greater_15m,
        "Vessels <15m": vessels_less_15m,
        "Missing or 0 Length": vessels_missing_length,
        "DWT Stats": filtered_data["Capacity - Dwt"].describe().to_dict(),
        "GT Stats": filtered_data["Capacity - Gt"].describe().to_dict(),
        "Length Stats": filtered_data["Length"].describe().to_dict(),
        "Draught Stats": filtered_data["Draught"].describe().to_dict(),
        "Average Speed Stats": filtered_data["Average Speed"].describe().to_dict(),
    }

# Vessel type counts with additional statistics
    vessel_type_counts = filtered_data.groupby(column).size()

    # Adjust min calculation to exclude zeros where applicable
    dwt_stats = filtered_data.groupby(column)["Capacity - Dwt"].agg(
        min=lambda x: x[x > 0].min() if (x > 0).any() else 0,
        max="max",
        mean=lambda x: x[x > 0].mean() if (x > 0).any() else 0
    )

    dwt_missing_counts = filtered_data.groupby(column)["Capacity - Dwt"].apply(
        lambda x: x.isna().sum() + (x <= 0).sum()
    )

    # Prepare vessel type table with new columns
    vessel_type_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Vessel Type"),
            html.Th("Count"),
            html.Th("DWT Range (Min - Max, Non-Zero)"),
            html.Th("Average DWT (Non-Zero)"),
            html.Th("Missing/Zero DWT Count")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(vessel_type),
                html.Td(count),
                html.Td(
                    f"{dwt_stats.loc[vessel_type, 'min']:.2f} - {dwt_stats.loc[vessel_type, 'max']:.2f}"
                    if not pd.isna(dwt_stats.loc[vessel_type, 'min']) else "N/A"
                ),
                html.Td(
                    f"{dwt_stats.loc[vessel_type, 'mean']:.2f}"
                    if not pd.isna(dwt_stats.loc[vessel_type, 'mean']) else "N/A"
                ),
                html.Td(dwt_missing_counts[vessel_type])
            ])
            for vessel_type, count in vessel_type_counts.items()
        ])
    ])


    # Prepare stats table
    stats_table = html.Table([
        html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
        html.Tbody([
            html.Tr([html.Td("Total Vessels"), html.Td(stats["Total Vessels"])]),
            html.Tr([html.Td("Vessels >15m"), html.Td(stats["Vessels >15m"])]),
            html.Tr([html.Td("Vessels <15m"), html.Td(stats["Vessels <15m"])]),
            html.Tr([html.Td("Missing or 0 Length"), html.Td(stats["Missing or 0 Length"])]),
        ])
    ])

    # Combine both tables
    return html.Div([
        html.H3("Vessel Statistics Summary"),
        stats_table,
        html.H3("Vessel Type Counts with DWT Statistics"),
        vessel_type_table
    ])



    # Prepare stats table
    stats_table = html.Table([
        html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
        html.Tbody([
            html.Tr([html.Td("Total Vessels"), html.Td(stats["Total Vessels"])]),
            html.Tr([html.Td("Vessels >15m"), html.Td(stats["Vessels >15m"])]),
            html.Tr([html.Td("Vessels <15m"), html.Td(stats["Vessels <15m"])]),
            html.Tr([html.Td("Missing or 0 Length"), html.Td(stats["Missing or 0 Length"])]),
        ])
    ])

    # Combine both tables
    return html.Div([
        html.H3("Vessel Statistics Summary"),
        stats_table,
        html.H3("Vessel Type Counts with DWT Statistics"),
        vessel_type_table
    ])

# (3) INSPECTOR PAGE
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

# (4) SFC PAGE
@app.callback(
    [Output("sfc-energy-histogram", "figure"),
     Output("sfc-energy-pie-chart", "figure"),
     Output("sfc-energy-bar-chart", "figure"),
     Output("sfc-fuel-type-bar-chart", "figure"),
     ],
    [Input("sfc-categorization-dropdown", "value")]
)
def update_sfc_analysis_charts(categorization):
    filtered_data = data.copy()

    # Handle categorization logic
    if categorization in ["Pacific - Simplified", "Pacific - Detailed"]:
        filtered_data[categorization] = filtered_data["Flag"].apply(lambda x: categorize_flag(x, categorization))
        filtered_data = filtered_data.dropna(subset=[categorization])
    elif categorization == "Pacific Only":
        filtered_data = filtered_data[filtered_data["Flag"].isin(PICTs)]
    elif categorization == "Other Only":
        filtered_data = filtered_data[~filtered_data["Flag"].isin(PICTs)]
    elif categorization == "All Countries":
        filtered_data = filtered_data.dropna(subset=["Flag"])

    # Create the histogram
    histogram_fig = px.histogram(
        filtered_data,
        x="Energy Consumption (TJ/year)",
        color=categorization if categorization in filtered_data.columns else "Flag",
        title=f"Histogram of Energy Consumption ({categorization})",
        labels={"Energy Consumption (TJ/year)": "Energy Consumption (TJ/year)"}
    )

    # Create the pie chart
    pie_chart_fig = px.pie(
        filtered_data,
        names=categorization if categorization in filtered_data.columns else "Flag",
        values="Energy Consumption (TJ/year)",
        title=f"Energy Consumption Distribution ({categorization})"
    )

    # Create the bar chart
    bar_chart_fig = px.bar(
        filtered_data,
        x=categorization if categorization in filtered_data.columns else "Flag",
        y="Energy Consumption (TJ/year)",
        color=categorization if categorization in filtered_data.columns else "Flag",
        title=f"Energy Consumption by {categorization}",
        labels={"x": categorization if categorization in filtered_data.columns else "Flag"}
    )

    # Create the new fuel-type bar chart
    fuel_type_bar_chart = px.bar(
        filtered_data,
        x="Vessel Type - Detailed",  # One bar per detailed vessel type
        y="Energy Consumption (TJ/year)",
        color="Fuel Type",  # Color bars based on fuel type
        title="Energy Consumption by Vessel Type (Color-coded by Fuel Type)",
        labels={"Fuel Type": "Fuel Type", "Energy Consumption (TJ/year)": "Energy Consumption (TJ/year)"},
        category_orders={"Fuel Type": list(fuel_type_mapping.values())}  # Consistent fuel type order
    )
    fuel_type_bar_chart.update_layout(
        xaxis={'categoryorder': 'total descending'},  # Sort bars by energy consumption
        template="plotly_white",
        xaxis_title="Vessel Type - Detailed",
        yaxis_title="Energy Consumption (TJ/year)"
    )

    return histogram_fig, pie_chart_fig, bar_chart_fig, fuel_type_bar_chart

# (5) MODELLING PAGE

# Determine suitability of each vessel type - detailed

decarbonisation_suitability = {
    "Yacht": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Electricity": 15, "HVO": 20, "Synthetic Diesel": 40, 
            "Bio-Ethanol": 15, "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "General Cargo": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 40, "HVO": 20, "Bio-LNG": 20,
            "Synthetic Diesel": 10, "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Research/Survey Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Combustion)": 20, "Methanol": 30, "HVO": 20,
            "Synthetic Diesel": 20, "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Supply Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 25, "Electricity": 20, 
            "Synthetic Diesel": 10, "Hydrogen (Fuel Cell)": 5
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Cable Layer": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 50, "HVO": 30, "Synthetic Diesel": 10,
            "Hydrogen (Combustion)": 5, "Hydrogen (Fuel Cell)": 5
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Military Ops": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "HVO": 50, "Ammonia": 30, "Synthetic Diesel": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": False,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Special Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Methanol": 30, "Bio-LNG": 30, "Electricity": 20,
            "Synthetic Diesel": 10, "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Ro-Ro/Vehicles Carrier": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 30, "Ammonia": 30, "Bio-LNG": 20,
            "Synthetic Diesel": 10, "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Container Ship": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 30, "Ammonia": 30, "Hydrogen (Combustion)": 20,
            "Bio-LNG": 10, "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Fishing Vessel": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20,
            "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Sailing Vessel": {
        "Current Fuel": "None (MGO auxiliary)",
        "Clean Fuels": {
            "Electricity": 50, "HVO": 30, "Synthetic Diesel": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Trawler": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "HVO": 40, "Bio-LNG": 30, "Synthetic Diesel": 20, "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Special Pleasure Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Electricity": 40, "HVO": 40, "Synthetic Diesel": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Special Cargo": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 40, "HVO": 20, "Bio-LNG": 20, "Synthetic Diesel": 10, 
            "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Other Special Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 30, "Electricity": 30, "HVO": 20, "Synthetic Diesel": 10, 
            "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Passenger Vessel": {
        "Current Fuel": "LFO",
        "Clean Fuels": {
            "Electricity": 30, "Bio-LNG": 30, "Hydrogen (Fuel Cell)": 20, 
            "HVO": 10, "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Crude Oil Tanker": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Ammonia": 40, "Methanol": 30, "Bio-LNG": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "Oil/Chemical Tanker": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 40, "Bio-LNG": 30, "Ammonia": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "LNG Tanker": {
        "Current Fuel": "LNG",
        "Clean Fuels": {
            "Bio-LNG": 60, "Ammonia": 30, "Hydrogen (Combustion)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Special Passenger Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Hydrogen (Fuel Cell)": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Anchor Handling Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 50, "HVO": 30, "Synthetic Diesel": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Barge": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Electricity": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Reefer": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Bio-LNG": 40, "Methanol": 40, "Synthetic Diesel": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "Tug": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Combustion)": 30, "Electricity": 30, "Methanol": 20, 
            "HVO": 20
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "LPG Tanker": {
        "Current Fuel": "LNG",
        "Clean Fuels": {
            "Hydrogen (Combustion)": 30, "Ammonia": 30, "Bio-LNG": 30, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Ro-Ro/Passenger Vessel": {
        "Current Fuel": "LFO",
        "Clean Fuels": {
            "Methanol": 30, "Hydrogen (Fuel Cell)": 25, "Bio-LNG": 25, 
            "HVO": 10, "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Bulk Carrier": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Ammonia": 40, "Methanol": 30, "Bio-LNG": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "Heavy Load Carrier": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Ammonia": 40, "Bio-LNG": 30, "Synthetic Diesel": 20, 
            "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "Oil Products Tanker": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 30, "Ammonia": 30, "Bio-LNG": 30, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": False,
        },
    },
    "Platform": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Passenger/Cargo Ship": {
        "Current Fuel": "LFO",
        "Clean Fuels": {
            "Methanol": 30, "Hydrogen (Fuel Cell)": 30, "Electricity": 30, 
            "Bio-LNG": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Fish Carrier": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Hydrogen (Combustion)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Training Ship": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Electricity": 30, "Methanol": 30, "HVO": 20, 
            "Synthetic Diesel": 10, "Hydrogen (Fuel Cell)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Landing Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Methanol": 40, "Electricity": 30, "HVO": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Fire Fighting Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Fuel Cell)": 40, "Electricity": 30, "Methanol": 20, 
            "HVO": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Offshore Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Special Fishing Vessel": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Hydrogen (Combustion)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Other Pleasure Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Electricity": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": True,
        },
    },
    "Patrol Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Hydrogen (Combustion)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": False,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Search & Rescue": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Bio-LNG": 40, "Hydrogen (Fuel Cell)": 30, "HVO": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": False,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Other Passenger": {
        "Current Fuel": "LFO",
        "Clean Fuels": {
            "Bio-LNG": 40, "Methanol": 30, "Hydrogen (Fuel Cell)": 20, 
            "HVO": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Other Fishing": {
        "Current Fuel": "MDO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Hydrogen (Combustion)": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Other Cargo": {
        "Current Fuel": "HFO",
        "Clean Fuels": {
            "Methanol": 40, "Bio-LNG": 30, "Synthetic Diesel": 20, 
            "Ammonia": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": True,
            "Sailing & Hybrid": True,
        },
    },
    "Service Vessel": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Pusher Tug": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Combustion)": 30, "Bio-LNG": 30, "Methanol": 20, 
            "HVO": 10, "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Unspecified": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Bio-LNG": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Electricity": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Pilot Boat": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Combustion)": 40, "Electricity": 30, "Methanol": 20, 
            "HVO": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": True,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "Navigation Aids": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Electricity": 40, "HVO": 30, "Synthetic Diesel": 20, 
            "Bio-Ethanol": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": False,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
    "High Speed Craft": {
        "Current Fuel": "MGO",
        "Clean Fuels": {
            "Hydrogen (Fuel Cell)": 40, "Electricity": 30, "HVO": 20, 
            "Synthetic Diesel": 10
        },
        "Efficiency Measures": {
            "Hull Coating & Propeller Upgrades": False,
            "Slow Steaming": False,
            "Sailing & Hybrid": False,
        },
    },
}

    # Emission intensities in g/MJ (CO₂, SOx, NOx, PM)

EMISSION_INTENSITIES = {
        "HFO": {"CO2": 77.4, "SOx": 2, "NOx": 1.8, "PM": 2.5},
        "LFO": {"CO2": 74.1, "SOx": 0.8, "NOx": 1.5, "PM": 0.5},
        "MDO": {"CO2": 73.5, "SOx": 0.5, "NOx": 1.5, "PM": 0.3},
        "MGO": {"CO2": 73.3, "SOx": 0.3, "NOx": 1.3, "PM": 0.3},
        "LNG": {"CO2": 56.1, "SOx": 0.01, "NOx": 0.5, "PM": 0.01},
        "Hydrogen": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.0, "PM": 0.0},
        "Biofuels": {"CO2": 10.0, "SOx": 0.1, "NOx": 0.2, "PM": 0.02},
        "Ammonia": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.1, "PM": 0.01},
        "Electricity": {"CO2": 0.0, "SOx": 0.0, "NOx": 0.0, "PM": 0.0},
        "Methanol": {"CO2": 22.0, "SOx": 0.05, "NOx": 0.3, "PM": 0.02},
    }

EFFICIENCIES = {
        "HFO": 0.40,
        "LFO": 0.40,
        "MDO": 0.40,
        "MGO": 0.40,
        "LNG": 0.45,
        "Hydrogen": 0.50,
        "Biofuels": 0.38,
        "Ammonia": 0.36,
        "Electricity": 0.90,
        "Methanol": 0.35,
    }

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
        State("hull-coating-adoption-rate", "value"),
        State("hull-coating-savings", "value"),
        State("slow-steaming-adoption-rate", "value"),
        State("slow-steaming-savings", "value"),
        State("sailing-hybrid-adoption-rate", "value"),
        State("sailing-hybrid-savings", "value"),
        State("clean-fuel-rate", "value"),
    ],
)
def calculate_decarbonisation_scenarios(
    start_clicks,
    abort_clicks,
    annual_growth_rate,
    end_year,
    hull_coating_adoption_rate,
    hull_coating_savings,
    slow_steaming_adoption_rate,
    slow_steaming_savings,
    sailing_hybrid_adoption_rate,
    sailing_hybrid_savings,
    clean_fuel_rate,
):
    start_year = 2025
    years = list(range(start_year, end_year + 1))

    global data

    # Efficiency measures
    efficiency_measures = [
        {
            "name": "Hull Coating & Propeller Upgrades",
            "adoption_rate": hull_coating_adoption_rate / 100,
            "savings": hull_coating_savings / 100,
        },
        {
            "name": "Slow Steaming",
            "adoption_rate": slow_steaming_adoption_rate / 100,
            "savings": slow_steaming_savings / 100,
        },
        {
            "name": "Sailing & Hybrid",
            "adoption_rate": sailing_hybrid_adoption_rate / 100,
            "savings": sailing_hybrid_savings / 100,
        },
    ]

    # Extract all possible fuels
    all_fuels = set(fuel_type_mapping.values()).union(
        fuel for vessel in decarbonisation_suitability.values() for fuel in vessel["Clean Fuels"]
    )
    
    # Initialize fuel_results
    fuel_results = {year: {fuel: 0 for fuel in all_fuels} for year in years}

    # Initialize vessel-specific results
    vessel_results = {year: {} for year in years}

    # Step 1: Organize data by vessel type
    for vessel_type, suitability in decarbonisation_suitability.items():
        current_fuel = fuel_type_mapping.get(vessel_type, "Unknown")
        annual_energy = data[data["Vessel Type - Detailed"] == vessel_type]["Energy Consumption (TJ/year)"].sum() or 0

        for year in years:
            # Apply annual growth rate
            if year == start_year:
                vessel_results[year][vessel_type] = {"energy": annual_energy, "fuel": current_fuel}
            else:
                previous_energy = vessel_results[year - 1][vessel_type]["energy"]
                vessel_results[year][vessel_type] = {"energy": previous_energy * (1 + annual_growth_rate / 100), "fuel": current_fuel}

    # Step 2: Apply efficiency measures
    for year in years[1:]:
        for vessel_type, suitability in decarbonisation_suitability.items():
            current_energy = vessel_results[year][vessel_type]["energy"]

            # Adjust energy for each efficiency measure
            for measure in efficiency_measures:
                if suitability["Efficiency Measures"][measure["name"]]:
                    adoption_rate = measure["adoption_rate"] ** (year - start_year)
                    adjusted_savings = min(adoption_rate * measure["savings"], 1.0)  # Cap at 100%
                    current_energy *= (1 - adjusted_savings)

            vessel_results[year][vessel_type]["energy"] = current_energy

    # Step 3: Apply clean fuel transition
    for year in years:
        for vessel_type, suitability in decarbonisation_suitability.items():
            current_energy = vessel_results[year][vessel_type]["energy"]
            current_fuel = vessel_results[year][vessel_type]["fuel"]

            # Apply clean fuel allocation
            total_clean_fuel_allocation = 0
            for clean_fuel, percentage in suitability["Clean Fuels"].items():
                allocation = current_energy * (percentage / 100) * (clean_fuel_rate / 100)
                fuel_results[year][clean_fuel] += allocation
                total_clean_fuel_allocation += allocation

            # Update fossil fuel allocation
            remaining_energy = max(current_energy - total_clean_fuel_allocation, 0)
            fuel_results[year][current_fuel] += remaining_energy

    # Step 4: Create DataFrame for Visualization
    results_df = pd.DataFrame.from_dict(fuel_results, orient="index").reset_index().rename(columns={"index": "Year"})

    # Create energy charts
    energy_bar_chart = px.bar(
        results_df.melt(id_vars="Year", var_name="Fuel Type", value_name="Energy (TJ)"),
        x="Year",
        y="Energy (TJ)",
        color="Fuel Type",
        title="Energy Consumption by Fuel Over Time",
    )

    energy_area_chart = px.area(
        results_df.melt(id_vars="Year", var_name="Fuel Type", value_name="Energy (TJ)"),
        x="Year",
        y="Energy (TJ)",
        color="Fuel Type",
        title="Energy Consumption Over Time (Area Chart)",
    )

    # Step 5: Prepare data for stacked bar chart (2025 vs Target Year)
    comparison_years = [2025, end_year]  # Start year and target year
    stacked_data = []

    for year in comparison_years:
        for vessel_type, suitability in decarbonisation_suitability.items():
            for fuel_type, fuel_consumption in fuel_results[year].items():
                stacked_data.append({
                    "Year": year,
                    "Vessel Type": vessel_type,
                    "Fuel Type": fuel_type,
                    "Fuel Consumption (TJ)": fuel_consumption,
                })

    # Convert to DataFrame
    stacked_df = pd.DataFrame(stacked_data)

    # Filter out zero consumption to simplify visualization
    stacked_df = stacked_df[stacked_df["Fuel Consumption (TJ)"] > 0]

    # Create stacked bar chart
    stacked_bar_chart = px.bar(
        stacked_df,
        x="Vessel Type",
        y="Fuel Consumption (TJ)",
        color="Fuel Type",
        facet_col="Year",
        barmode="relative",
        title="Fuel Consumption by Vessel Type (2025 vs Target Year)",
        labels={
            "Fuel Consumption (TJ)": "Fuel Consumption (TJ)",
            "Vessel Type": "Vessel Type",
            "Fuel Type": "Fuel Type",
        },
    )

    # Customize layout for readability
    stacked_bar_chart.update_layout(
        xaxis_title="Vessel Type",
        yaxis_title="Fuel Consumption (TJ)",
        legend_title="Fuel Type",
        template="plotly_white",
        margin={"r": 0, "t": 40, "l": 40, "b": 80},
    )


    # Progress values
    progress_value = str(len(years))
    progress_max = str(len(years))

    return progress_value, progress_max, html.Div([
        dcc.Graph(figure=energy_bar_chart),
        dcc.Graph(figure=energy_area_chart),
        dcc.Graph(figure=stacked_bar_chart),
    ])

#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

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
    app.run(debug=True)