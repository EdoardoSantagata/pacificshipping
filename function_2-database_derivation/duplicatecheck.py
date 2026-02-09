import pandas as pd

# Load the Excel file
file_path = "pacific_shipping_database.xlsx" #"Pacific Shipping Database - FINAL (for paper).xlsx"
sheet_name = "extracted" #"COMPLETE - Data Handle"

# Read the data
try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
except Exception as e:
    print(f"Error loading file or sheet: {e}")
    exit()

# Check the first few rows and column names to verify the data
print("Columns in the dataset:", df.columns)

# Identify duplicates based on all columns
all_duplicates = df[df.duplicated(keep=False)]

# Identify duplicates based on specific columns (e.g., "Vessel Name" and "Flag")
if "Vessel Name" in df.columns and "Flag" in df.columns:
    subset_duplicates = df[df.duplicated(subset=["Vessel Name", "Flag"], keep=False)]
    unique_vessels = df.drop_duplicates(subset=["Vessel Name", "Flag"])
    num_unique_vessels = len(unique_vessels)
else:
    print("Columns 'Vessel Name' and 'Flag' are not in the dataset. Cannot check for subset duplicates.")
    subset_duplicates = pd.DataFrame()
    num_unique_vessels = 0

# Print results
print(f"Total rows in dataset: {len(df)}")
print(f"Total duplicates (all columns): {len(all_duplicates)}")
if not subset_duplicates.empty:
    print(f"Total duplicates (based on 'Vessel Name' and 'Flag'): {len(subset_duplicates)}")
    print(f"Total unique vessels (based on 'Vessel Name' and 'Flag'): {num_unique_vessels}")
else:
    print("No subset duplicates could be identified.")

# Save duplicates to a new Excel file for inspection
output_file = "Duplicates_Report.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    all_duplicates.to_excel(writer, sheet_name="All Duplicates", index=False)
    if not subset_duplicates.empty:
        subset_duplicates.to_excel(writer, sheet_name="Subset Duplicates", index=False)

print(f"Duplicate data has been saved to {output_file}.")
