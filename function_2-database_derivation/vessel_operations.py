import requests
from datetime import datetime, timedelta
import csv
import os
import pandas as pd
from tqdm import tqdm
import time

# Your API key
API_KEY = #insert API key
BASE_REPORT_URL = "https://api.datalastic.com/api/v0/report"

# Function to split date range into chunks
def split_date_range(start_date, end_date, delta=30):
    date_ranges = []
    current_start = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=delta), end_date)
        date_ranges.append((current_start.date().isoformat(), current_end.date().isoformat()))
        current_start = current_end + timedelta(days=1)
    return date_ranges

# Function to fetch vessel historical data
def get_vessel_history(identifier, identifier_type, start_date, end_date):
    url = "https://api.datalastic.com/api/v0/vessel_history"
    date_ranges = split_date_range(start_date, end_date)
    positions = []
    
    # --- Clean identifier ---
    if identifier_type.lower() == "imo":
        try:
            # Cast to int first to remove .0, then back to str
            identifier = str(int(float(identifier)))
        except ValueError:
            identifier = str(identifier)  # fallback

    for start, end in date_ranges:
        params = {
            "api-key": API_KEY,
            identifier_type: identifier,
            "from": start,
            "to": end
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            positions.extend(data.get("data", {}).get("positions", []))
        except requests.exceptions.RequestException as e:
            print(f"Error for {identifier_type.upper()} {identifier} ({start} to {end}): {e}")
    return positions

# Function to calculate days underway
def calculate_days_underway(positions):
    underway_dates = set()
    for position in positions:
        speed = position.get("speed", 0)
        timestamp = position.get("last_position_UTC")
        # Ensure speed is a valid number and timestamp is not None
        if speed is not None and speed > 0 and timestamp:
            try:
                date = datetime.fromisoformat(timestamp.replace("Z", "")).date()
                underway_dates.add(date)
            except ValueError:
                print(f"Invalid timestamp format: {timestamp}")
    return len(underway_dates)

# Function to save positions to a CSV file
def save_positions_to_csv(positions, identifier, ship_name, country_iso, identifier_type):
    # Ensure the directory exists
    output_dir = "apidata"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    filename = os.path.join(output_dir, f"{identifier}_{ship_name}_{country_iso}.csv")
    
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow([
            "Latitude", "Longitude", "Speed", "Course", "Heading", "Destination", 
            "Timestamp", "Status"
        ])
        # Write each position
        for pos in positions:
            speed = pos.get("speed", 0)
            if speed is None:
                speed = 0  # Default to 0 if speed is None
            status = "Underway" if speed > 0 else "Stationary"
            writer.writerow([
                pos.get("lat"),
                pos.get("lon"),
                speed,
                pos.get("course"),
                pos.get("heading"),
                pos.get("destination"),
                pos.get("last_position_UTC"),
                status
            ])
    print(f"Data saved to {filename}")

# Function to calculate average speed
def calculate_average_speed(positions):
    """
    Calculate the average speed of the ship from the API data.
    Includes only speeds > 0 and with 'Underway' status.
    """
    underway_speeds = []
    for pos in positions:
        speed = pos.get("speed", 0)
        if speed is not None and speed > 0:  # Check explicitly for None and compare
            underway_speeds.append(speed)
    
    if underway_speeds:
        return sum(underway_speeds) / len(underway_speeds)
    return "No data"


# Main function to process ships
def process_ships(database_file, start_date, end_date, row_limit=None):
    # Load the dataset
    df = pd.read_excel(database_file, sheet_name="Sheet1")
    
    # Select columns of interest
    columns_of_interest = [
        "Flag", "Vessel Name", "Imo", "Mmsi", "Vessel Type - Generic", 
        "Vessel Type - Detailed", "Capacity - Dwt", "Capacity - Gt", "Length", 
        "Draught", "Average Speed", "Commercial Market", "Built", 
        "Capacity - Liquid Gas", "Capacity - Liquid Oil", "Capacity - Passengers"
    ]
    df = df[columns_of_interest]
    
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
        "Fishing Vessel": "MGO",
        "Sailing Vessel": "None",  # Primarily wind-powered
        "Trawler": "MGO",
        "Special Pleasure Craft": "MGO",
        "Special Cargo": "HFO",
        "Other Special Craft": "MGO",
        "Passenger Vessel": "LFO",
        "Crude Oil Tanker": "HFO",
        "Oil/Chemical Tanker": "HFO",
        "LNG Tanker": "LNG",
        "Special Passenger Vessel": "MGO",
        "Anchor Handling Vessel": "MGO",
        "Barge": "MDO",
        "Reefer": "HFO",
        "Tug": "MGO",
        "LPG Tanker": "LNG",
        "Ro-Ro/Passenger Vessel": "LFO",
        "Bulk Carrier": "HFO",
        "Heavy Load Carrier": "HFO",
        "Oil Products Tanker": "HFO",
        "Platform": "MDO",
        "Passenger/Cargo Ship": "LFO",
        "Fish Carrier": "MGO",
        "Training Ship": "MGO",
        "Landing Craft": "MGO",
        "Fire Fighting Vessel": "MGO",
        "Offshore Vessel": "MGO",
        "Special Fishing Vessel": "MGO",
        "Other Pleasure Craft": "MGO",
        "Patrol Vessel": "MGO",
        "Search & Rescue": "MGO",
        "Other Passenger": "LFO",
        "Other Fishing": "MGO",
        "Other Cargo": "HFO",
        "Service Vessel": "MGO",
        "Pusher Tug": "MGO",
        "Unspecified": "MDO",
        "Pilot Boat": "MGO",
        "Navigation Aids": "MGO",
        "High Speed Craft": "MGO",
    }


    # Limit rows for testing if specified
    if row_limit:
        df = df.head(row_limit)
    
    # Add columns for operational days, data status, and API average speed
    df["Operational Days"] = "No data"
    df["Data Status"] = "No data"
    df["Average Speed API"] = "No data"
    
    # Process each ship
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing Ships", unit="ship"):
        # Default data status
        data_status = "No Data"
        
        # Attempt using IMO first
        print(f"Processing ship: {row['Vessel Name']} (IMO: {row['Imo']})")
        positions = get_vessel_history(row["Imo"], "imo", start_date, end_date)
        identifier_type = "imo"
        identifier = row["Imo"]
        
        if positions:
            data_status = "IMO Data Found"
        else:
            # Fallback to MMSI if no IMO data
            if pd.notna(row["Mmsi"]):
                print(f"No data for IMO {row['Imo']}. Trying MMSI: {row['Mmsi']}")
                positions = get_vessel_history(row["Mmsi"], "mmsi", start_date, end_date)
                identifier_type = "mmsi"
                identifier = row["Mmsi"]
                if positions:
                    data_status = "MMSI Data Found"
        
        # Save operational days and .csv file if data is available
        if positions:
            # Calculate operational days
            days_underway = calculate_days_underway(positions)
            df.at[index, "Operational Days"] = days_underway
            
            # Save individual CSV file
            save_positions_to_csv(positions, identifier, row["Vessel Name"], row["Flag"], identifier_type)
            
            # Calculate average speed
            avg_speed = calculate_average_speed(positions)
            df.at[index, "Average Speed API"] = avg_speed
        else:
            print(f"No data found for both IMO {row['Imo']} and MMSI {row['Mmsi']}.")
        
        # Update data status
        df.at[index, "Data Status"] = data_status

        # Add a new column for estimated fuel type
    if "Vessel Type - Detailed" in df.columns:
        df["Estimated Fuel Type"] = df["Vessel Type - Detailed"].map(fuel_type_mapping).fillna("Unknown")
    else:
        raise KeyError("The column 'Vessel Type - Detailed' is missing from the dataset.")

    # Save results to a new sheet
    with pd.ExcelWriter(database_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="final", index=False)
    print(f"Results saved to sheet 'final' in {database_file}")



# Run the process for a range of ships - MAIN PROGRAM
if __name__ == "__main__":
    start_time = time.time()  # Start timing
    
    database_file = "finaloutputapistuff.xlsx"
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    row_limit = 0  # Adjust this for testing (None for all rows)
    
    process_ships(database_file, start_date, end_date, row_limit)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")





# Additional optional function to run

def check_ship_existence(identifier, identifier_type):
    url = f"https://api.datalastic.com/api/v0/vessel"
    params = {
        "api-key": API_KEY,
        identifier_type: identifier
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Data found for {identifier_type.upper()} {identifier}: {data}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"No data found for {identifier_type.upper()} {identifier}: {e}")
        return None

#check_ship_existence("9375898", "imo")    #if we want to check if there is data that exists for a particular ship, we can use both imo and mmsi ni case there are name discrepancies
#check_ship_existence("546025400", "mmsi")

#print("Payload:", payload)
