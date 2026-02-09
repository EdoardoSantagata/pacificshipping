import requests

#Datalastic API Key
API_KEY = #insert API key
DATALASTIC_PORT_API_URL = 'https://api.datalastic.com/api/v0/port_find'

#function to check availability using Datalastic API with country-specific checks
def check_port_or_anchorage(location_name, port_type="Port", country_iso=None):
    try:
        params = {
            "api-key": API_KEY,
            "name": location_name,
            "fuzzy": 0,  #exact match, set 1 for fuzzy
            "port_type": port_type
        }
        
        if country_iso:
            params["country_iso"] = country_iso  #restrict the search to the specified country

        response = requests.get(DATALASTIC_PORT_API_URL, params=params)
        response.raise_for_status()  #raise an error if the status code isn't 200

        data = response.json()

        if data["meta"]["success"] and data["data"]:
            location_info = data["data"][0]
            print(f"{location_name} found! Details: {location_info}")
        else:
            print(f"{location_name} not found in the database.")
            
    except Exception as e:
        print(f"Error checking {location_name}: {e}")

#list of ports and anchorages with their corresponding countries
ports_and_anchors = {
    "VAVOUTO": "NC",  # New Caledonia
    "VAVOUTO ANCH": "NC",  # Italy (this would depend on actual knowledge of location)
    "NEPOUI": "NC",  # New Caledonia
    "NEPOUI ANCH": "NC",  # New Caledonia
    "LAE": "PG",  # Papua New Guinea
    "LAE ANCH": "PG"  # Papua New Guinea
}

#check for each port and anchorage
for location, country_iso in ports_and_anchors.items():
    print(f"\nChecking {location} (Port) in {country_iso}:")
    check_port_or_anchorage(location, port_type="Port", country_iso=country_iso)  #checking as a port
    print(f"\nChecking {location} (Anchorage) in {country_iso}:")
    check_port_or_anchorage(location, port_type="Anchorage", country_iso=country_iso)  #checking as an anchorage

#problematic ports in Datalastic that need additional inspection for validation
coordinates = {
    "VAVOUTO": (-21.0025, 164.6786),  #approximate coordinates for Vavouto, New Caledonia
    "VAVOUTO ANCH": (-21.0025, 164.6786),  #approximate coordinates for Vavouto Anchorage
    "NEPOUI": (-21.3284, 164.9939),  #approximate coordinates for Nepoui, New Caledonia
    "NEPOUI ANCH": (-21.3284, 164.9939),  #approximate coordinates for Nepoui Anchorage
    "LAE": (-6.7411, 146.9966),  #approximate coordinates for Lae, Papua New Guinea
    "LAE ANCH": (-6.8048, 146.9688),  #approximate coordinates for Lae Anchorage
}

#function to check availability using Datalastic API by coordinates
def check_port_or_anchorage_by_coords(lat, lon, radius=15, port_type="Port"):
    try:
        params = {
            "api-key": API_KEY,
            "lat": lat,
            "lon": lon,
            "radius": radius,  #radius in nautical miles
            "port_type": port_type
        }

        response = requests.get(DATALASTIC_PORT_API_URL, params=params)
        response.raise_for_status()  #raise an error if the status code isn't 200

        data = response.json()

        if data["meta"]["success"] and data["data"]:
            location_info = data["data"]
            for loc in location_info:
                print(f"Found {port_type} near {lat}, {lon}: {loc}")
        else:
            print(f"No {port_type} found within {radius} nautical miles of coordinates {lat}, {lon}.")
            
    except Exception as e:
        print(f"Error checking coordinates {lat}, {lon}: {e}")

#check for each port and anchorage by coordinates
for location, (lat, lon) in coordinates.items():
    print(f"\nChecking {location} (Port) near coordinates {lat}, {lon}:")
    check_port_or_anchorage_by_coords(lat, lon, port_type="Port")  #checking as a port
    print(f"\nChecking {location} (Anchorage) near coordinates {lat}, {lon}:")
    check_port_or_anchorage_by_coords(lat, lon, port_type="Anchorage")  #checking as an anchorage
