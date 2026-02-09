import geopy.distance
from geopy.geocoders import Nominatim
import time
import requests
import pandas as pd

geolocator = Nominatim(user_agent="port_distance_calculator")

#datalastic API endpoint for Port Finder
DATALASTIC_PORT_API_URL = "https://api.datalastic.com/api/v0/port_find"

#API key for Datalastic
API_KEY = #insert API key

#ports in various countries
ports = {
    "OFU": "American Samoa",
    "PAGO PAGO": "American Samoa",
    "TAU": "American Samoa",
    "AITUTAKI": "Cook Islands",
    "ATIU": "Cook Islands",
    "MANGAIA": "Cook Islands",
    "MAUKE ISLAND": "Cook Islands",
    "MITIARO ISLAND": "Cook Islands",
    "RAROTONGA": "Cook Islands",
    "CICIA": "Fiji",
    "LABASA": "Fiji",
    "LAUTOKA": "Fiji",
    "LEVUKA": "Fiji",
    "MANA ISLAND": "Fiji",
    "MAOLO LAILAI ISLAND": "Fiji",
    "MOALA": "Fiji",
    "NABOUWALU": "Fiji",
    "NADI": "Fiji",
    "NATOVI": "Fiji",
    "RABI": "Fiji",
    "SAVUSAVU": "Fiji",
    "SINGATOKA": "Fiji",
    "SUVA": "Fiji",
    "TAVUKI": "Fiji",
    "TURTLE ISLAND": "Fiji",
    "VANUA MBALAVU": "Fiji",
    "VATULELE": "Fiji",
    "VUDA": "Fiji",
    "WAIRIKI": "Fiji",
    "YASAWA ISLAND": "Fiji",
    "ATUONA": "French Polynesia",
    "BORA BORA": "French Polynesia",
    "FATU HIVA": "French Polynesia",
    "HIVA OA": "French Polynesia",
    "MAUPITI": "French Polynesia",
    "PAPEETE": "French Polynesia",
    "ROTOAVA": "French Polynesia",
    "TAIOHAE": "French Polynesia",
    "TETIAROA": "French Polynesia",
    "UA HUKA": "French Polynesia",
    "UA POU": "French Polynesia",
    "UTUROA": "French Polynesia",
    "VAIARE HARBOR": "French Polynesia",
    "GUAM": "Guam",
    "BETIO": "Kiribati",
    "TABUAERAN": "Kiribati",
    "AILUK ISLAND": "Marshall Islands",
    "ARNO": "Marshall Islands",
    "ENEWETAK ISLAND": "Marshall Islands",
    "ENYU AIRFIELD": "Marshall Islands",
    "KWAJALEIN": "Marshall Islands",
    "LIKIEP ISLAND": "Marshall Islands",
    "MAJURO": "Marshall Islands",
    "MALOELAP ISLAND": "Marshall Islands",
    "MEJIT ISLAND": "Marshall Islands",
    "MILI ISLAND": "Marshall Islands",
    "NAMU": "Marshall Islands",
    "RONGELAP ISLAND": "Marshall Islands",
    "UTIRIK ISLAND": "Marshall Islands",
    "WOTHO ISLAND": "Marshall Islands",
    "WOTJE ISLAND": "Marshall Islands",
    "CHUUK": "Micronesia",
    "KOSRAE": "Micronesia",
    "POHNPEI": "Micronesia",
    "TOMIL": "Micronesia",
    "ROTA": "N Mariana Is",
    "SAIPAN": "N Mariana Is",
    "TINIAN": "N Mariana Is",
    "NAURU ISLAND": "Nauru",
    "BAIE DE PRONY": "New Caledonia",
    "BAIE NGO": "New Caledonia",
    "EASO": "New Caledonia",
    "ILE DES PINS": "New Caledonia",
    "KOUAOUA": "New Caledonia",
    "KOUMAC": "New Caledonia",
    "MONEO": "New Caledonia",
    "NEPOUI": "New Caledonia",
    "NOUMEA": "New Caledonia",
    "OUINNE": "New Caledonia",
    "OUVEA": "New Caledonia",
    "PAAGUMENE": "New Caledonia",
    "PORO": "New Caledonia",
    "TADINE": "New Caledonia",
    "TANLE": "New Caledonia",
    "THIO": "New Caledonia",
    "KONE": "New Caledonia", #Marinetraffic says VAVOUTO, but in Datalastsic it is KONE
    "ALOFI": "Niue",
    "NIUE ISLAND": "Niue",
    "ANGAUR": "Palau",
    "KOROR": "Palau",
    "MELEKEOK": "Palau",
    "ALOTAU": "Papua New Guinea",
    "BASAMUK": "Papua New Guinea",
    "BIALLA": "Papua New Guinea",
    "BUKA": "Papua New Guinea",
    "DARU": "Papua New Guinea",
    "KAVIENG": "Papua New Guinea",
    "KEREMA": "Papua New Guinea",
    "KIETA": "Papua New Guinea",
    "KIMBE": "Papua New Guinea",
    "KIUNGA": "Papua New Guinea",
    "KUMUL": "Papua New Guinea",
    "LAE": "Papua New Guinea",
    "LESE": "Papua New Guinea",
    "LIHIR ISLAND": "Papua New Guinea",
    "MADANG": "Papua New Guinea",
    "MOROBE": "Papua New Guinea",
    "ORO BAY": "Papua New Guinea",
    "PORT MORESBY": "Papua New Guinea",
    "RABAUL": "Papua New Guinea",
    "UMUDA": "Papua New Guinea",
    "VANIMO": "Papua New Guinea",
    "WEWAK": "Papua New Guinea",
    "PITCAIRN": "Pitcairn Is",
    "APIA": "Samoa",
    "AOLA BAY": "Solomon Islands",
    "AUKI": "Solomon Islands",
    "GIZO": "Solomon Islands",
    "HONIARA": "Solomon Islands",
    "KIRAKIRA": "Solomon Islands",
    "MALLOCO BAY": "Solomon Islands",
    "NORO": "Solomon Islands",
    "RANNELL ISLAND": "Solomon Islands",
    "RINGGI COVE": "Solomon Islands",
    "TULAGI": "Solomon Islands",
    "VIRU HARBOUR": "Solomon Islands",
    "YANDINA": "Solomon Islands",
    "ATAFU": "Tokelau",
    "FAKAOFO": "Tokelau",
    "NUKUNOMU": "Tokelau",
    "EUA ISLAND": "Tonga",
    "NEIAFU": "Tonga",
    "NUKU ALOFA": "Tonga",
    "TONGA": "Tonga",
    "FUNAFUTI": "Tuvalu",
    "ANEITYUM": "Vanuatu",
    "CRAIG COVE": "Vanuatu",
    "MAEWO": "Vanuatu",
    "PORT VILA": "Vanuatu",
    "SANTO": "Vanuatu",
    "FUTUNA ISLAND": "Wallis Futuna Is",
    "MATA UTU": "Wallis Futuna Is",
    "WALLIS ISLAND APT": "Wallis Futuna Is"
}

#anchorages in various countries
anchorages = {
    "PAGO PAGO ANCH": "American Samoa",
    "AITUTAKI ANCH": "Cook Islands",
    "RAROTONGA ANCH": "Cook Islands",
    "LABASA ANCH": "Fiji",
    "LAUTOKA ANCH": "Fiji",
    "LEVUKA ANCH": "Fiji",
    "NADI BAY ANCH": "Fiji",
    "SUVA ANCH": "Fiji",
    "ATUONA BAY ANCH": "French Polynesia",
    "FATU HIVA ANCH": "French Polynesia",
    "ROTOAVA ANCH": "French Polynesia",
    "TARAWA ANCH": "Kiribati",
    "KWAJALEIN ANCH": "Marshall Islands",
    "MAJURO ANCH": "Marshall Islands",
    "KOLONIA ANCH": "Micronesia",
    "TOMIL ANCH": "Micronesia",
    "SAIPAN ANCH": "N Mariana Is",
    "BAIE DE PRONY ANCH": "New Caledonia",
    "KOUAOUA ANCH": "New Caledonia",
    # "NEPOUI ANCH": "New Caledonia", #does not exist in Datalastic server
    "NOUMEA ANCH": "New Caledonia",
    "PAAGUMENE ANCH": "New Caledonia",
    "THIO ANCH": "New Caledonia",
    "KONE ANCH": "New Caledonia", #Marinetraffic says "VAVOUTO ANCH": "New Caledonia", but Datalastic says KONE ANCH
    "ALOFI ANCH": "Niue",
    "KIETA ANCH": "Papua New Guinea",
    "KUMUL ANCH": "Papua New Guinea",
    "LAE ANCH": "Papua New Guinea",
    "LESE ANCH": "Papua New Guinea",
    "LIHIR ISLAND ANCH": "Papua New Guinea",
    "MADANG ANCH": "Papua New Guinea",
    "PORT MORESBY ANCH": "Papua New Guinea",
    "RABAUL ANCH": "Papua New Guinea",
    "UMUDA ANCH": "Papua New Guinea",
    "VANIMO ANCH": "Papua New Guinea",
    "WEWAK ANCH": "Papua New Guinea",
    "HONIARA ANCH": "Solomon Islands",
    "NORO ANCH": "Solomon Islands",
    "NEIAFU ANCH": "Tonga",
    "NUKU ALOFA ANCH": "Tonga",
    "ESPIRITU SANTO ANCH": "Vanuatu",
    "PORT VILA ANCH": "Vanuatu"
}

#shelters (without corresponding ports)
shelters = {
    "LIFOU": "New Caledonia",
    "MOULY": "New Caledonia"
}

#marinas (without corresponding ports)
marinas = {
    "OPUNOHU BAY": "French Polynesia"
}

#match anchorages to port
anchorage_to_port = {
    "PAGO PAGO ANCH": "PAGO PAGO",
    "AITUTAKI ANCH": "AITUTAKI",
    "RAROTONGA ANCH": "RAROTONGA",
    "LABASA ANCH": "LABASA",
    "LAUTOKA ANCH": "LAUTOKA",
    "LEVUKA ANCH": "LEVUKA",
    "NADI BAY ANCH": "NADI",
    "SUVA ANCH": "SUVA",
    "ATUONA BAY ANCH": "ATUONA",
    "FATU HIVA ANCH": "FATU HIVA",
    "ROTOAVA ANCH": "ROTOAVA",
    "TARAWA ANCH": "BETIO",
    "KWAJALEIN ANCH": "KWAJALEIN",
    "MAJURO ANCH": "MAJURO",
    "KOLONIA ANCH": "POHNPEI",
    "TOMIL ANCH": "TOMIL",
    "SAIPAN ANCH": "SAIPAN",
    "BAIE DE PRONY ANCH": "BAIE DE PRONY",
    "KOUAOUA ANCH": "KOUAOUA",
    #"NEPOUI ANCH": "NEPOUI", #anchorage does not exist in Datalastic server - checked manually
    "NOUMEA ANCH": "NOUMEA",
    "PAAGUMENE ANCH": "PAAGUMENE",
    "THIO ANCH": "THIO",
    "KONE ANCH": "KONE", #adjusted based on name in Datalastic
    "ALOFI ANCH": "ALOFI",
    "KIETA ANCH": "KIETA",
    "KUMUL ANCH": "KUMUL",
    "LAE ANCH": "LAE",
    "LESE ANCH": "LESE",
    "LIHIR ISLAND ANCH": "LIHIR ISLAND",
    "MADANG ANCH": "MADANG",
    "PORT MORESBY ANCH": "PORT MORESBY",
    "RABAUL ANCH": "RABAUL",
    "UMUDA ANCH": "UMUDA",
    "VANIMO ANCH": "VANIMO",
    "WEWAK ANCH": "WEWAK",
    "HONIARA ANCH": "HONIARA",
    "NORO ANCH": "NORO",
    "NEIAFU ANCH": "NEIAFU",
    "NUKU ALOFA ANCH": "NUKU ALOFA",
    "PORT VILA ANCH": "PORT VILA",
    "ESPIRITU SANTO ANCH": "ESPIRITU SANTO"
}

#function to get coordinates from Datalastic Port Finder API
def get_coordinates_from_port_finder(location_name, port_type="Port"):
    try:
        #API request parameters
        params = {
            "api-key": API_KEY,
            "name": location_name,
            "fuzzy": 0,  #set to 1 if you want fuzzy search
            "port_type": port_type  #for ports, use "Port"; for anchorages, use "Anchorage"
        }

        #send request to Datalastic API
        response = requests.get(DATALASTIC_PORT_API_URL, params=params)
        response.raise_for_status()  #check for query errors
        
        data = response.json()
        
        if data["meta"]["success"] and data["data"]:
            port_info = data["data"][0]
            latitude = port_info.get("lat")
            longitude = port_info.get("lon")
            country = port_info.get("country_name")  #extract country information
            
            if latitude and longitude and country:
                return latitude, longitude, country
            else:
                print(f"No coordinates found for {location_name}.")
                return None
        else:
            print(f"Unable to find {location_name} in the port database.")
            return None
    except Exception as e:
        print(f"Error getting coordinates from Datalastic API for {location_name}: {e}")
        return None

#function to calculate distance between port and anchorage using Datalastic coordinates
def calculate_distance(port, anchorage):
    #get coordinates and country for both port and anchorage
    port_coords = get_coordinates_from_port_finder(port)
    anchorage_coords = get_coordinates_from_port_finder(anchorage, port_type="Anchorage")
    
    if port_coords and anchorage_coords:
        #unpack latitude, longitude, and country
        port_lat, port_lon, port_country = port_coords
        anchorage_lat, anchorage_lon, anchorage_country = anchorage_coords
        
        #validate countries
        if port_country != anchorage_country:
            print(f"Country mismatch: {port} is in {port_country}, but {anchorage} is in {anchorage_country}. Skipping distance calculation.")
            return None
        
        #calculate the distance in nautical miles
        dist = geopy.distance.distance((port_lat, port_lon), (anchorage_lat, anchorage_lon)).nautical
        print(f"Distance from {anchorage} to {port}: {dist:.2f} nautical miles")
        return {"Anchorage": anchorage, "Port": port, "Distance (NM)": round(dist, 2)}
    else:
        print(f"Unable to calculate distance for {anchorage} and {port}")
        return None


def save_port_distances_to_excel(port_data, file_name="port_distances.xlsx"):
    try:
        df = pd.DataFrame(port_data)
        print(f"Saving the following data to Excel:\n{df}")
        df.to_excel(file_name, index=False)
        print(f"Port distances saved to {file_name}.")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


#list to store distance data
port_data_list = []

#loop through anchorages and use the matching dictionary
for anchorage in anchorages:
    port = anchorage_to_port.get(anchorage)  #sse the anchorage_to_port dictionary to get the port
    if port:
        anchorage_country = anchorages[anchorage]
        port_country = ports.get(port)
        
        #validate countries from the dictionaries
        if anchorage_country != port_country:
            print(f"Country mismatch in dictionaries: {port} is listed in {port_country}, but {anchorage} is listed in {anchorage_country}.")
            continue  # Skip to the next anchorage-port pair if there's a mismatch
        
        print(f"\nChecking distance for anchorage {anchorage} and port {port}")
        distance_data = calculate_distance(port, anchorage)
        
        #append distance data to the list
        if distance_data:
            port_data_list.append(distance_data)
            print(f"Added distance data: {distance_data}")
    else:
        print(f"Port for anchorage {anchorage} not found in the anchorage_to_port dictionary.")
    time.sleep(1)  #to avoid API rate limits


#save port distances to an Excel file
if port_data_list:
    save_port_distances_to_excel(port_data_list)
else:
    print("No distance data collected to save.")

#function to save all port coordinates to an Excel file
def save_port_coordinates_to_excel(ports, file_name="port_coordinates.xlsx"):
    port_coords_list = []
    
    for port, country in ports.items():
        print(f"Fetching coordinates for port: {port}")
        port_coords = get_coordinates_from_port_finder(port)
        
        if port_coords:
            port_lat, port_lon, port_country = port_coords
            port_coords_list.append({
                "Port Name": port,
                "Country": port_country,
                "Latitude": port_lat,
                "Longitude": port_lon
            })
            print(f"Added port data: {port_coords_list[-1]}")
        else:
            print(f"Coordinates not found for port: {port}")
        time.sleep(1)  # To avoid API rate limits
    
    if port_coords_list:
        try:
            df = pd.DataFrame(port_coords_list)
            print(f"Saving the following data to Excel:\n{df}")
            df.to_excel(file_name, index=False)
            print(f"Port coordinates saved to {file_name}.")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
    else:
        print("No port coordinates collected to save.")

#save all port coordinates to an Excel file
save_port_coordinates_to_excel(ports)
