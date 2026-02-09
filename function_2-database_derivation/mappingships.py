import os
import pandas as pd
import folium

# Folder containing the CSV files
folder_path = "apidata"

# Create a Folium map centered on a general location (adjust as needed)
ship_map = folium.Map(location=[-35.0, 174.0], zoom_start=8)

# Iterate over all CSV files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        # Read the CSV file
        file_path = os.path.join(folder_path, filename)
        data = pd.read_csv(file_path)

        # Filter rows where the ship status is "Underway"
        underway_data = data[data['Status'] == "Underway"]

        # Add a small dot for each underway location
        for _, row in underway_data.iterrows():
            latitude = row['Latitude']
            longitude = row['Longitude']
            
            # Adjust longitude if negative
            if longitude < 0:
                longitude += 360

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=1,  # Small dot
                color='blue',
                fill=True,
                fill_opacity=0.8
            ).add_to(ship_map)

# Save the map to an HTML file
output_path = "ship_map.html"
ship_map.save(output_path)
print(f"Map saved to {output_path}")
