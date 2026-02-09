import pandas as pd
import requests

# Configuration
API_KEY = #insert API key
INPUT_FILE = "uuids.xlsx"
OUTPUT_FILE = "vesselsfound.xlsx"
API_URL = "https://api.datalastic.com/api/v0/vessel_info"

# Step 1: Read UUIDs from the input Excel file
data = pd.read_excel(INPUT_FILE)
uuids = data['uuid'].tolist()
total_uuids = len(uuids)  # Total number of UUIDs to process
# Step 2: Prepare a list to store results
vessel_info = []

# Step 3: Query the Datalastic API for each UUID
for idx, uuid in enumerate(uuids, start=1):  # Use enumerate to track progress . old: for uuid in uuids:
    try:
        # API request for vessel info
        response = requests.get(f"{API_URL}?api-key={API_KEY}&uuid={uuid}")
        response.raise_for_status()  # Raise error for HTTP issues
        
        # Parse the JSON response
        response_json = response.json()
        if response_json.get("data"):
            vessel_data = response_json["data"]
            vessel_info.append({
                'uuid': uuid,
                'country_iso': vessel_data.get("country_iso", "Unknown"),
                'name': vessel_data.get("name", "Unknown"),
                'imo': vessel_data.get("imo", "Unknown"),
                'mmsi': vessel_data.get("mmsi", "Unknown"),
                'type': vessel_data.get("type", "Unknown"),
                'type_specific': vessel_data.get("type_specific", "Unknown"),
                'gross_tonnage': vessel_data.get("gross_tonnage", "Unknown"),
                'deadweight': vessel_data.get("deadweight", "Unknown"),
                'teu': vessel_data.get("teu", "Unknown"),
                'liquid_gas': vessel_data.get("liquid_gas", "Unknown"),
                'length': vessel_data.get("length", "Unknown"),
                'breadth': vessel_data.get("breadth", "Unknown"),
                'draught_avg': vessel_data.get("draught_avg", "Unknown"),
                'draught_max': vessel_data.get("draught_max", "Unknown"),
                'speed_avg': vessel_data.get("speed_avg", "Unknown"),
                'speed_max': vessel_data.get("speed_max", "Unknown"),
                'year_built': vessel_data.get("year_built", "Unknown"),
                'home_port': vessel_data.get("home_port", "Unknown"),
                'is_navaid': vessel_data.get("is_navaid", "Unknown"),
                'activity_status': vessel_data.get("activity_status", "Unknown")
            })
        else:
            vessel_info.append({
                'uuid': uuid,
                'country_iso': 'Not Found',
                'name': 'Not Found',
                'imo': 'Not Found',
                'mmsi': 'Not Found',
                'type': 'Not Found',
                'type_specific': 'Not Found',
                'gross_tonnage': 'Not Found',
                'deadweight': 'Not Found',
                'teu': 'Not Found',
                'liquid_gas': 'Not Found',
                'length': 'Not Found',
                'breadth': 'Not Found',
                'draught_avg': 'Not Found',
                'draught_max': 'Not Found',
                'speed_avg': 'Not Found',
                'speed_max': 'Not Found',
                'year_built': 'Not Found',
                'home_port': 'Not Found',
                'is_navaid': 'Not Found',
                'activity_status': 'Not Found'
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for UUID {uuid}: {e}")
        vessel_info.append({
            'uuid': uuid,
            'country_iso': 'Error',
            'name': 'Error',
            'imo': 'Error',
            'mmsi': 'Error',
            'type': 'Error',
            'type_specific': 'Error',
            'gross_tonnage': 'Error',
            'deadweight': 'Error',
            'teu': 'Error',
            'liquid_gas': 'Error',
            'length': 'Error',
            'breadth': 'Error',
            'draught_avg': 'Error',
            'draught_max': 'Error',
            'speed_avg': 'Error',
            'speed_max': 'Error',
            'year_built': 'Error',
            'home_port': 'Error',
            'is_navaid': 'Error',
            'activity_status': 'Error'
        })
    print(f"Processed {idx}/{total_uuids} UUIDs")

# Step 4: Save results to an Excel file
df_output = pd.DataFrame(vessel_info)
df_output.to_excel(OUTPUT_FILE, index=False)

print(f"Vessel data saved to {OUTPUT_FILE}")
