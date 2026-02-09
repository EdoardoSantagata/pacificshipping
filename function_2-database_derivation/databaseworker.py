import pandas as pd

# Load the Excel file
file_path = "pacific_shipping_database.xlsx"
excel_data = pd.ExcelFile(file_path)

# Load the relevant sheets
df_origin = excel_data.parse("origin")
df_current = excel_data.parse("current")
df_destination = excel_data.parse("destination")
df_previous_to_origin = excel_data.parse("previous to origin")
df_ports = excel_data.parse("ports")
df_types = excel_data.parse("types")

# Add operator ships
df_operator = excel_data.parse("operator")

# Strip spaces from column names to avoid mismatches
df_ports.columns = df_ports.columns.str.strip()
df_types.columns = df_types.columns.str.strip()
df_previous_to_origin.columns = df_previous_to_origin.columns.str.strip()

# Rename columns for consistency (if needed)
df_ports.rename(columns={'Type': 'type', 'Port': 'port'}, inplace=True)
df_types.rename(columns={'Considered': 'considered?'}, inplace=True)
df_previous_to_origin.rename(columns={'Previous To Origin Port': 'Previous to Origin Port'}, inplace=True)

# Define valid port types to include
valid_port_types = ["Port", "Anchorage", "Shelter"]

# Filter the ports sheet to include only valid port types
if 'type' in df_ports.columns and 'port' in df_ports.columns:
    valid_ports = df_ports[df_ports['type'].isin(valid_port_types)]['port'].tolist()
else:
    raise KeyError("The expected columns 'type' or 'port' are missing from the 'ports' sheet.")

# Filter vessel types
if 'considered?' in df_types.columns and 'Vessel Type - Detailed' in df_types.columns:
    valid_types = df_types[df_types['considered?'] == "YES"]["Vessel Type - Detailed"].tolist()
else:
    raise KeyError("The expected columns 'considered?' or 'Vessel Type - Detailed' are missing from the 'types' sheet.")

# Define a function to filter each sheet
def filter_ships(df, port_column, sheet_name):
    initial_count = len(df)

    # Step 1: Filter ships based on the relevant port
    if port_column not in df.columns:
        raise KeyError(f"Column '{port_column}' is missing from the sheet.")
    df_filtered = df[df[port_column].isin(valid_ports)]
    port_filtered_count = len(df_filtered)

    # Step 2: Remove ships without a flag
    df_filtered = df_filtered[df_filtered["Flag"].notna() & (df_filtered["Flag"] != "0")]
    flag_filtered_count = len(df_filtered)

    # Step 3: Filter ships based on vessel type
    if "Vessel Type - Detailed" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Vessel Type - Detailed"].isin(valid_types)]
        type_filtered_count = len(df_filtered)
    else:
        type_filtered_count = port_filtered_count  # No change if column is missing

    # Print filtering statistics
    print(f"{sheet_name}:")
    print(f"  Initial count: {initial_count}")
    print(f"  After port filtering: {port_filtered_count} ({initial_count - port_filtered_count} filtered out)")
    print(f"  After flag filtering: {flag_filtered_count} ({port_filtered_count - flag_filtered_count} filtered out)")
    print(f"  After type filtering: {type_filtered_count} ({flag_filtered_count - type_filtered_count} filtered out)")

    return df_filtered

# Apply the filter function to each data sheet
df_origin_filtered = filter_ships(df_origin, "Origin Port", "Origin Sheet")
df_current_filtered = filter_ships(df_current, "Current Port", "Current Sheet")
df_destination_filtered = filter_ships(df_destination, "Destination Port", "Destination Sheet")
df_previous_to_origin_filtered = filter_ships(df_previous_to_origin, "Previous to Origin Port", "Previous to Origin Sheet")

# Filter for operator ships to ensure only filtered by types
def filter_operator_ships(df, sheet_name):
    initial_count = len(df)

    # Filter ships based on vessel type
    if "Vessel Type - Detailed" in df.columns:
        df_filtered = df[df["Vessel Type - Detailed"].isin(valid_types)]
        type_filtered_count = len(df_filtered)
    else:
        raise KeyError(f"Column 'Vessel Type - Detailed' is missing from the '{sheet_name}' sheet.")

    # Print filtering statistics
    print(f"{sheet_name}:")
    print(f"  Initial count: {initial_count}")
    print(f"  After type filtering: {type_filtered_count} ({initial_count - type_filtered_count} filtered out)")

    return df_filtered


# Filter the operator sheet by type
df_operator_filtered = filter_operator_ships(df_operator, "Operator Sheet")


# Combine all the filtered dataframes
combined_df = pd.concat([
    df_origin_filtered, 
    df_current_filtered, 
    df_destination_filtered, 
    df_previous_to_origin_filtered,
    df_operator_filtered  # Include the filtered operator data
], ignore_index=True)

# Remove duplicates based on "Vessel Name" and "Flag"
unique_ships = combined_df.drop_duplicates(subset=["Vessel Name", "Flag"])

# Write the result to the "filtered" sheet in the Excel file
with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    unique_ships.to_excel(writer, sheet_name="filtered", index=False)

# Print final statistics
print("\nFinal Statistics:")
print(f"Total ships after filtering: {len(unique_ships)}")
print(f"Duplicates removed: {len(combined_df) - len(unique_ships)}")
print("Filtered data has been written to the 'filtered' sheet.")
