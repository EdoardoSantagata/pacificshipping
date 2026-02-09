import folium
from folium import Element
import searoute as sr
import math
from folium.map import LayerControl
from folium import Map, Element

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


#hardcoded port coordinates
city_coords = {
    "Suva, Fiji": (-18.1248, 178.4501),
    "Auckland, New Zealand": (-36.8485, 174.7831),
    "Sydney, Australia": (-33.8688, 151.2093),
    "Noumea, New Caledonia": (-22.2558, 166.4505),
    "Sri Racha, Thailand": (13.159, 100.928),
    "Kaohsiung, Taiwan": (22.6163, 120.3133),
    "Changsu, China": (31.653, 120.553),
    "Yokohama, Japan": (35.4437, 139.638),
    "Osaka, Japan": (34.6937, 135.5023),
    "Busan, South Korea": (35.1796, 129.0756),
    "Lae, Papua New Guinea": (-6.722, 146.984),
    "Motukea, Papua New Guinea": (-9.4669, 147.1504),
    "Timaru, New Zealand": (-44.3967, 171.2543),
    "Tauranga, New Zealand": (-37.6878, 176.1651),
    "Marsden Point, New Zealand": (-35.846, 174.493),
    "Prony Bay, New Caledonia": (-22.3333, 166.8833),
    "Subic Bay, Philippines": (14.7945, 120.2745),
    "Singapore": (1.3521, 103.8198),
    "Jakarta, Indonesia": (-6.2088, 106.8456),
    "Port Klang, Malaysia": (3.0008, 101.3834),
    "Honiara, Solomon Islands": (-9.428, 159.9492),
    "Adelaide, Australia": (-34.9285, 138.6007),
    "Fremantle, Australia": (-32.0568, 115.7431),
    "Townsville, Australia": (-19.259, 146.817),
    "Lautoka, Fiji": (-17.6156, 177.4505),
    "Brisbane, Australia": (-27.4698, 153.0251),
    "Melbourne, Australia": (-37.8136, 144.9631),
    "Long Beach, USA": (33.7701, -118.1937 + 360),
    "Oakland, USA": (37.8044, -122.2711 + 360),
    "Papeete, French Polynesia": (-17.5516, -149.5585 + 360),
    "Apia, Samoa": (-13.8333, -171.7667 + 360),
    "Pago Pago, American Samoa": (-14.2781, -170.702 + 360),
    "Rarotonga, Cook Islands": (-21.2292, -159.7762 + 360),
    "Aitutaki, Cook Islands": (-18.8303, -159.7642 + 360),
    "Niue": (-19.0544, -169.8672 + 360),
    "Vava'u, Tonga": (-18.6435, -173.991 + 360),
    "Nuku'alofa, Tonga": (-21.1393, -175.204 + 360),
    "Lyttleton, New Zealand": (-43.6076, 172.7192),
    "Napier, New Zealand": (-39.4928, 176.9120),
    "Nelson, New Zealand": (-41.2706, 173.2840),
    "Santo, Vanuatu": (-15.5333, 167.1667),
    "Port Vila, Vanuatu": (-17.7333, 168.3167),
    "Kimbe, Papua New Guinea": (-5.5507, 150.1411),
    "Buka, Papua New Guinea": (-5.4322, 154.6738),
    "Rabaul, Papua New Guinea": (-4.207, 152.1705),
    "Kavieng, Papua New Guinea": (-2.5803, 150.7967),
    "Wewak, Papua New Guinea": (-3.5535, 143.6336),
    "Oro Bay, Papua New Guinea": (-8.8933, 148.5339),
    "Alotau, Papua New Guinea": (-10.3094, 150.4591),
    "Madang, Papua New Guinea": (-5.2203, 145.7851),
    "Shanghai, China": (31.2304, 121.4737),
    "Ningbo, China": (29.8683, 121.5439),
    "Nansha, China": (22.8038, 113.6094),
    "Hong Kong SAR": (22.3193, 114.1694),
    "Tuvalu": (-8.5201, 179.1940), #funafuti
    "Nauru": (-0.5228, 166.9315),
    "Hakata, Japan": (33.5902, 130.4206),
    "Guam": (13.4443, 144.7937),
    "Saipan, Northern Mariana Islands": (15.1850, 145.7467),
    "Tianjin, China": (39.3434, 117.3616),
    "Qingdao, China": (36.0671, 120.3826),
    "Kobe, Japan": (34.6901, 135.1955),
    "Nagoya, Japan": (35.1815, 136.9066),
    "Tarawa, Kiribati": (1.4518, 173.0327),
    "Majuro, Marshall Islands": (7.0906, 171.3806),
    "Surabaya, Indonesia": (-7.2575, 112.7521),
    "Gladstone, Australia": (-23.8420, 151.2534),
    "Seattle, USA": (47.6062, -122.3321 + 360),
    "Los Angeles, USA": (34.0522, -118.2437 + 360),
    "Vancouver, Canada": (49.2827, -123.1207 + 360),
    "Wallis, Wallis and Futuna": (-13.2816, -176.1745 + 360),
    "Futuna, Wallis and Futuna": (-14.2938, -178.1165 + 360),
    "Mount Maunganui, New Zealand": (-37.6355, 176.1815),
    "Kiritimati, Kiribati": (1.8709, -157.3630 + 360),
    "Metroport, Auckland, New Zealand": (-36.8439, 174.7575),
    "Kosrae, Micronesia": (5.3167, 162.9833),
    "Pohnpei, Micronesia": (6.8541, 158.2624),
    "Newcastle, Australia": (-32.9283, 151.7817),
    "Wellington, New Zealand": (-41.2865, 174.7762),
    "Yap, Micronesia": (9.5149, 138.1265),
    "Koror, Palau": (7.3426, 134.4789),
    "Okinawa, Japan": (26.3344, 127.8056),
    "Honolulu, Hawaii": (21.3069, -157.8583 + 360),
    "Tinian, Northern Mariana Islands": (15.0000, 145.6190),
    "Chuuk, Micronesia": (7.4167, 151.7833),
    "Ebeye, Marshall Islands": (9.7881, 167.7381),
    "Kwajalein, Marshall Islands": (8.7207, 167.7316),
    "Tacoma, USA": (47.2529, -122.4443 + 360),
    "Tanjung Pelepas, Malaysia": (1.3627, 103.5357),
    "Noro, Solomon Islands": (-8.2372, 157.1964),
    "Chofu, Japan": (33.9763, 131.2787),
    "Moji, Japan": (33.9225, 130.9520),
    "Fakaofo, Tokelau": (-9.3653, -171.2458 + 360),
    "Nukunonu, Tokelau": (-9.2000, -171.8333 + 360),
    "Atafu, Tokelau": (-8.5421, -172.5000 + 360),
    "Mangareva, French Polynesia": (-23.1130, -134.9702 + 360),
    "Pitcairn Island": (-25.0660, -130.1005 + 360),
    "Manzanillo, Panama": (9.3642, -79.8952 + 360),
    "Savannah, USA": (32.08, -81.09 + 360),
    "Kingston, Jamaica": (17.98, -76.80 + 360),
    "Xingang, China": (39.0839, 117.2160),
}

#searoute dictionary with swapped long lat
searoute_coords = {city: (lon, lat) for city, (lat, lon) in city_coords.items()}

#print(searoute_coords) - activate to check the coordinates in terminal

#hardcoded services under each operator
service_to_operator = {
    # Swire Shipping
    "North Asia Service": "Swire Shipping",
    "Pacific Islands Service": "Swire Shipping",
    "North Asia Express": "Swire Shipping",
    "Pacific Weekly Express": "Swire Shipping",
    "PNG Service": "Swire Shipping",
    "US West Coast - Pacific Islands Service": "Swire Shipping",
    "Micronesia Service": "Swire Shipping",
    "Pacific North Asia Service - Loop 1": "Swire Shipping",
    "Pacific North Asia Service - Loop 2": "Swire Shipping",
    "Pacific North Asia Service - Loop 3": "Swire Shipping",
    "New Zealand Eastern Pacific Service": "Swire Shipping",
    
    # ANL Shipping
    "APR Service": "ANL",
    "NZ-Fiji Service ANL": "ANL",
    "PCX Service": "ANL",
    "Tahiti Service": "ANL",
    "WESTPAC Service": "ANL",
    "AUSPAC Service": "ANL",
    "SOUTHPAC Service": "ANL",
    "ANZ Shuttle Service": "ANL",
    "ANZ Wallis-Futuna Service": "ANL",
    "ANZPAC Service": "ANL",
    
    # NPDL Shipping
    "NZ-Fiji Service NPDL": "NPDL",
    "NZ-Samoa, American Samoa, Tonga Service": "NPDL",
    "NZ-New Caledonia, Vanuatu Service": "NPDL",
    "NZ-Vanuatu Service": "NPDL",
    "NZ-Tahiti Service": "NPDL",
    "NZ-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "NZ-Marshall Islands, Micronesia, Solomon Islands Service": "NPDL",
    "NZ-Cook Islands Service": "NPDL",
    "NZ-Honiara Service": "NPDL",
    "AUS-Fiji, Samoa, Tonga Service": "NPDL",
    "AUS-Tahiti, Tonga Service": "NPDL",
    "AUS-New Caledonia Service": "NPDL",
    "AUS-Vanuatu Service": "NPDL",
    "AUS-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "AUS-Solomon Islands Service": "NPDL",
    "AUS-Cook Islands Service": "NPDL",
    "FJ-Samoa, American Samoa, Tonga, NZ Service": "NPDL",
    "FJ-AUS Service": "NPDL",
    "FJ-Vanuatu Service": "NPDL",
    "FJ-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "FJ-Marshall Islands, Micronesia, Solomon Islands Service": "NPDL",
    "Samoa, American Samoa, Tonga-NZ, AUS Service": "NPDL",
    "New Caledonia-NZ Service": "NPDL",
    "Vanuatu-NZ Service": "NPDL",
    "New Caledonia, Vanuatu-NZ Service": "NPDL",
    "New Caledonia-Wallis and Futuna, Vanuatu Service": "NPDL",
    "New Caledonia-Fiji, Wallis and Futuna Service": "NPDL",
    "CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service": "NPDL",
    "CALPAC US-NZ, AUS Service": "NPDL",
    "CALPAC US-New Caledonia, Vanuatu Service": "NPDL",
    "CALPAC Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "CALPAC AUS, NZ, Fiji, Tahiti-US Service": "NPDL",
    "South Pacific Service": "NPDL",
    
    # Mariana Express Shipping
    "NZ-Guam, Saipan, Micronesia": "MELL",
    
    # Matson Shipping
    "Matson South Pacific Shipping Service": "Matson",
    "Matson Guam and Micronesia Shipping Service": "Matson",
    
    # MAERSK Shipping
    "Fiji Express Service": "MAERSK",
    "PNG Express Service": "MAERSK",
    
    # PIL Shipping - converted to MELL to better represent feeder and service vessels
    "ANA Service": "PIL",
    "MXS Service": "PIL",
    "EMS Service": "PIL",
    "MSP Service": "PIL",
    
    # Kyowa Shipping
    "Saipan, Guam, Micronesia Service": "Kyowa Shipping",
    "South Pacific Islands Service": "Kyowa Shipping",
    "PNG-AUS Service": "Kyowa Shipping",
    
    # Nauru Shipping Line
    "NSL Micronesian Pride Service": "Nauru Shipping Line",
    "NSL Supplementary Service": "Nauru Shipping Line",
    
    # Government of Tokelau
    "Department of Transport & Support Services Service": "Government of Tokelau",
    
    # Government of the Pitcairn Islands
    "MV Silver Supporter Regular Service": "Government of the Pitcairn Islands",
    "MV Silver Supporter NZ Freight Run Service": "Government of the Pitcairn Islands",
}

operator_colors = {
    "Swire Shipping": "red",
    "ANL": "blue",
    "NPDL": "green",
    "MELL": "pink",
    "Matson": "orange",
    "MAERSK": "purple",
    "PIL": "brown",
    "Kyowa Shipping": "yellow",
    "Nauru Shipping Line": "cyan",
    "Government of Tokelau": "cadetblue",
    "Government of the Pitcairn Islands": "beige",
    "CMA CGM": "grey",
    "NYK": "darkblue",
    "ONE": "lightgrey",
    "PFL": "black",
    "MSC": "darkgreen",
    "Carpenters Shipping": "lightblue",
}

#defining routes between ports for mapping with closed loop (returning to initial port)
routes = {

    #SWIRE SHIPPING
    "North Asia Service": [
        "Sri Racha, Thailand",
        "Kaohsiung, Taiwan",
        "Changsu, China",
        "Yokohama, Japan",
        "Osaka, Japan",
        "Busan, South Korea",
        "Lae, Papua New Guinea",
        "Motukea, Papua New Guinea",
        "Noumea, New Caledonia",
        "Auckland, New Zealand",
        "Timaru, New Zealand",
        "Tauranga, New Zealand",
        "Marsden Point, New Zealand",
        "Noumea, New Caledonia",
        "Prony Bay, New Caledonia",
        "Subic Bay, Philippines",
        "Sri Racha, Thailand",
    ],
    "US West Coast - Pacific Islands Service": [
        "Long Beach, USA",
        "Oakland, USA",
        "Papeete, French Polynesia",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Long Beach, USA",
    ],
    "North Asia Express": [
        "Shanghai, China",
        "Ningbo, China",
        "Nansha, China",
        "Hong Kong SAR",
        "Lae, Papua New Guinea",
        "Motukea, Papua New Guinea",
        "Townsville, Australia",
        "Shanghai, China",
    ],
    "Pacific Weekly Express": [
        "Port Klang, Malaysia",
        "Singapore",
        "Jakarta, Indonesia",
        "Motukea, Papua New Guinea",
        "Lae, Papua New Guinea",
        "Noumea, New Caledonia",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Honiara, Solomon Islands",
        "Rabaul, Papua New Guinea",
        "Madang, Papua New Guinea",
        "Port Klang, Malaysia",
    ],
    "PNG Service": [
        "Sydney, Australia",
        "Melbourne, Australia",
        "Brisbane, Australia",
        "Motukea, Papua New Guinea",
        "Lae, Papua New Guinea",
        "Honiara, Solomon Islands",
        "Sydney, Australia",
    ],
    "Pacific Islands Service": [
        "Sydney, Australia",
        "Melbourne, Australia",
        "Brisbane, Australia",
        "Prony Bay, New Caledonia",
        "Noumea, New Caledonia",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Port Vila, Vanuatu",
        "Sydney, Australia",
    ],
    "Micronesia Service": [
        "Busan, South Korea",
        "Hakata, Japan",
        "Yokohama, Japan",
        "Guam",
        "Saipan, Northern Mariana Islands",
        "Busan, South Korea",
    ],
    "Pacific North Asia Service - Loop 1": [
        "Kaohsiung, Taiwan",
        "Tianjin, China",
        "Qingdao, China",
        "Busan, South Korea",
        "Yokohama, Japan",
        "Port Vila, Vanuatu",
        "Noumea, New Caledonia",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Nuku'alofa, Tonga",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Santo, Vanuatu",
        "Kaohsiung, Taiwan",
    ],
    "Pacific North Asia Service - Loop 2": [
        "Busan, South Korea",
        "Kobe, Japan",
        "Nagoya, Japan",
        "Yokohama, Japan",
        "Honiara, Solomon Islands",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
        "Noumea, New Caledonia",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Nuku'alofa, Tonga",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Papeete, French Polynesia",
        "Tarawa, Kiribati",
        "Busan, South Korea",
    ],
    "Pacific North Asia Service - Loop 3": [
        "Busan, South Korea",
        "Majuro, Marshall Islands",
        "Tarawa, Kiribati",
        "Lae, Papua New Guinea",
        "Busan, South Korea",
    ],
    "New Zealand Eastern Pacific Service": [
        "Auckland, New Zealand",
        "Nuku'alofa, Tonga",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Papeete, French Polynesia",
        "Rarotonga, Cook Islands",
        "Aitutaki, Cook Islands",
        "Niue",
        "Nuku'alofa, Tonga",
        "Vava'u, Tonga",
        "Auckland, New Zealand",
    ],

    #ANL
    "APR Service": [
        "Port Klang, Malaysia",
        "Singapore",
        "Jakarta, Indonesia",
        "Surabaya, Indonesia",
        "Madang, Papua New Guinea",
        "Lae, Papua New Guinea",
        "Rabaul, Papua New Guinea",
        "Kimbe, Papua New Guinea",
        "Motukea, Papua New Guinea",
        "Townsville, Australia",
        "Gladstone, Australia",
        "Port Klang, Malaysia",
    ],
    "NZ-Fiji Service ANL": [
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Tauranga, New Zealand",
    ],
    "PCX Service": [
        "Vancouver, Canada",
        "Oakland, USA",
        "Los Angeles, USA",
        "Auckland, New Zealand",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Adelaide, Australia",
        "Tauranga, New Zealand",
        "Seattle, USA",
        "Oakland, USA",
        "Los Angeles, USA",
        "Auckland, New Zealand",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Tauranga, New Zealand",
        "Papeete, French Polynesia",
        "Vancouver, Canada",
    ],
    "Tahiti Service": [
        "Auckland, New Zealand",
        "Papeete, French Polynesia",
        "Auckland, New Zealand",
    ],
    "WESTPAC Service": [
        "Auckland, New Zealand",
        "Noumea, New Caledonia",
        "Brisbane, Australia",
        "Townsville, Australia",
        "Motukea, Papua New Guinea",
        "Lae, Papua New Guinea",
        "Kimbe, Papua New Guinea",
        "Rabaul, Papua New Guinea",
        "Honiara, Solomon Islands",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
    ],
    "AUSPAC Service": [
        "Melbourne, Australia",
        "Sydney, Australia",
        "Brisbane, Australia",
        "Noumea, New Caledonia",
        "Port Vila, Vanuatu",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
        "Melbourne, Australia",
    ],
    "SOUTHPAC Service": [
        "Auckland, New Zealand",
        "Nuku'alofa, Tonga",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Auckland, New Zealand",
    ],
    "ANZ Shuttle Service": [
        "Brisbane, Australia",
        "Noumea, New Caledonia",
        "Tauranga, New Zealand",
        "Brisbane, Australia",
    ],
    "ANZ Wallis-Futuna Service": [
        "Melbourne, Australia",
        "Sydney, Australia",
        "Brisbane, Australia",
        "Suva, Fiji",
        "Auckland, New Zealand", #workaround so no branches
        "Suva, Fiji",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Suva, Fiji"
    ],
    "ANZPAC Service": [
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
        "Tauranga, New Zealand",
    ],

    #NPDL Shipping
    "NZ-Fiji Service NPDL": [
        "Lyttleton, New Zealand",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
    ],
    "NZ-Samoa, American Samoa, Tonga Service": [
        "Lyttleton, New Zealand",
        "Auckland, New Zealand",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
    ],
    "NZ-New Caledonia, Vanuatu Service": [
        "Lyttleton, New Zealand",
        "Mount Maunganui, New Zealand",
        "Auckland, New Zealand",
        "Noumea, New Caledonia",
        "Lautoka, Fiji", #this should be a branch
        "Suva, Fiji",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
    ],
    "NZ-Vanuatu Service": [
        "Lyttleton, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Port Vila, Vanuatu",
        "Santo, Vanuatu",
    ],
    "NZ-Tahiti Service": [
        "Lyttleton, New Zealand",
        "Auckland, New Zealand",
        "Papeete, French Polynesia",
    ],
    "NZ-Tuvalu, Wallis and Futuna, Kiribati Service": [
        "Lyttleton, New Zealand",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Tuvalu",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Tarawa, Kiribati",
        "Kiritimati, Kiribati",
    ],
    "NZ-Marshall Islands, Micronesia, Solomon Islands Service": [
        "Metroport, Auckland, New Zealand",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Majuro, Marshall Islands",
        "Kosrae, Micronesia",
        "Pohnpei, Micronesia",
        "Honiara, Solomon Islands",
    ],
    "NZ-Cook Islands Service": [
        "Auckland, New Zealand",
        "Rarotonga, Cook Islands",
        "Aitutaki, Cook Islands",
    ],
    "NZ-Honiara Service": [
        "Mount Maunganui, New Zealand",
        "Auckland, New Zealand",
        "Honiara, Solomon Islands",
    ],
    "AUS-Fiji, Samoa, Tonga Service": [
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
    ],
    "AUS-Tahiti, Tonga Service": [
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Auckland, New Zealand",
        "Papeete, French Polynesia",
        "Nuku'alofa, Tonga",
    ],
    "AUS-New Caledonia Service": [
        "Brisbane, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Auckland, New Zealand",
        "Noumea, New Caledonia",
    ],
    "AUS-Vanuatu Service": [
        "Brisbane, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
    ],
    "AUS-Tuvalu, Wallis and Futuna, Kiribati Service": [
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Suva, Fiji",
        "Tuvalu",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Tarawa, Kiribati",
        "Kiritimati, Kiribati",
    ],
    "AUS-Solomon Islands Service": [
        "Melbourne, Australia",
        "Sydney, Australia",
        "Brisbane, Australia",
        "Honiara, Solomon Islands",
    ],
    "AUS-Cook Islands Service": [
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Auckland, New Zealand",
        "Rarotonga, Cook Islands",
        "Aitutaki, Cook Islands",
    ],
    "FJ-Samoa, American Samoa, Tonga, NZ Service": [
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
        "Tauranga, New Zealand",
        "Metroport, Auckland, New Zealand",
    ],
    "FJ-AUS Service": [
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Tauranga, New Zealand",
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
    ],
    "FJ-Vanuatu Service": [
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
    ],
    "FJ-Tuvalu, Wallis and Futuna, Kiribati Service": [
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Tuvalu",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Tarawa, Kiribati",
        "Kiritimati, Kiribati",
    ],
    "FJ-Marshall Islands, Micronesia, Solomon Islands Service": [
        "Suva, Fiji",
        "Majuro, Marshall Islands",
        "Kosrae, Micronesia",
        "Pohnpei, Micronesia",
        "Honiara, Solomon Islands",
    ],
    "Samoa, American Samoa, Tonga-NZ, AUS Service": [
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Nuku'alofa, Tonga",
        "Tauranga, New Zealand",
        "Metroport, Auckland, New Zealand",
        "Brisbane, Australia",
        "Newcastle, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
    ],
    "New Caledonia-NZ Service": [
        "Noumea, New Caledonia",
        "Suva, Fiji",
        "Tauranga, New Zealand",
    ],
    "Vanuatu-NZ Service": [
        "Port Vila, Vanuatu",
        "Santo, Vanuatu",
        "Suva, Fiji",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
    ],
    "New Caledonia, Vanuatu-NZ Service": [
        "Noumea, New Caledonia",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
        "Auckland, New Zealand",
    ],
    "New Caledonia-Wallis and Futuna, Vanuatu Service": [
        "Noumea, New Caledonia",
        "Suva, Fiji",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Suva, Fiji",
        "Port Vila, Vanuatu",
        "Santo, Vanuatu",
    ],
    "New Caledonia-Fiji, Wallis and Futuna Service": [
        "Noumea, New Caledonia",
        "Suva, Fiji",
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
    ],
    "CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service": [
        "Long Beach, USA",
        "Oakland, USA",
        "Papeete, French Polynesia",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Apia, Samoa",
        "Nuku'alofa, Tonga",
    ],
    "CALPAC US-NZ, AUS Service": [
        "Long Beach, USA",
        "Oakland, USA",
        "Apia, Samoa",
        "Tauranga, New Zealand",
        "Metroport, Auckland, New Zealand",
        "Brisbane, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
    ],
    "CALPAC US-New Caledonia, Vanuatu Service": [
        "Long Beach, USA",
        "Oakland, USA",
        "Suva, Fiji",
        "Apia, Samoa",
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Port Vila, Vanuatu",
        "Santo, Vanuatu",
        "Noumea, New Caledonia",
    ],
    "CALPAC Tuvalu, Wallis and Futuna, Kiribati Service": [
        "Long Beach, USA",
        "Oakland, USA",
        "Suva, Fiji",
        "Apia, Samoa",
        "Tauranga, New Zealand",
        "Suva, Fiji",
        "Tuvalu", 
        "Wallis, Wallis and Futuna",
        "Futuna, Wallis and Futuna",
        "Tarawa, Kiribati",
        "Kiritimati, Kiribati",
    ],
    "CALPAC AUS, NZ, Fiji, Tahiti-US Service": [
        "Brisbane, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Apia, Samoa",
        "Papeete, French Polynesia",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Long Beach, USA",
        "Oakland, USA",
    ],
    "South Pacific Service": [
        "Nansha, China",
        "Hong Kong SAR",
        "Lae, Papua New Guinea",
        "Honiara, Solomon Islands",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Tarawa, Kiribati",
        "Majuro, Marshall Islands",
        "Kosrae, Micronesia",
        "Pohnpei, Micronesia",
    ],

    #Mariana Express Shipping
    "NZ-Guam, Saipan, Micronesia": [
        "Auckland, New Zealand",
        "Lyttleton, New Zealand",
        "Wellington, New Zealand",
        "Napier, New Zealand",
        "Metroport, Auckland, New Zealand",
        "Tauranga, New Zealand",
        "Hong Kong SAR",
        "Guam",
        "Saipan, Northern Mariana Islands",
        "Yap, Micronesia",
        "Koror, Palau",
    ],

    #Matson Shipping
    "Matson South Pacific Shipping Service": [
        "Auckland, New Zealand",
        "Nuku'alofa, Tonga",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Niue",
        "Vava'u, Tonga",
        "Nuku'alofa, Tonga",
        "Vava'u, Tonga", #workaround to avoid branches
        "Niue", 
        "Pago Pago, American Samoa", 
        "Rarotonga, Cook Islands",
        "Aitutaki, Cook Islands",
        "Nuku'alofa, Tonga",
        "Lautoka, Fiji",
        "Brisbane, Australia",
        "Sydney, Australia", 
        "Melbourne, Australia", 
        "Lautoka, Fiji",
        "Sydney, Australia", 
        "Lautoka, Fiji",
        "Melbourne, Australia",
    ],
    "Matson Guam and Micronesia Shipping Service": [
        "Long Beach, USA",
        "Shanghai, China",
        "Ningbo, China",
        "Okinawa, Japan",
        "Okinawa, Japan",
        "Guam",
        "Saipan, Northern Mariana Islands", 
        "Tinian, Northern Mariana Islands", #avoid branches here too
        "Saipan, Northern Mariana Islands",
        "Guam",
        "Honolulu, Hawaii",
        "Oakland, USA",
        "Long Beach, USA",
        "Honolulu, Hawaii",
        "Long Beach, USA",
        "Honolulu, Hawaii",
        "Tacoma, USA",
        "Oakland, USA",
        "Honolulu, Hawaii",
        "Guam",
        "Yap, Micronesia",
        "Koror, Palau",
        "Yap, Micronesia",
        "Guam",
        "Chuuk, Micronesia",
        "Pohnpei, Micronesia",
        "Kosrae, Micronesia",
        "Majuro, Marshall Islands",
        "Ebeye, Marshall Islands",
        "Kwajalein, Marshall Islands",
        "Guam",
    ],

    #MAERSK
    "Fiji Express Service": [
        "Tauranga, New Zealand",
        "Auckland, New Zealand",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Tauranga, New Zealand",
    ],
    "PNG Express Service": [
        "Tanjung Pelepas, Malaysia",
        "Motukea, Papua New Guinea",
        "Noro, Solomon Islands",
        "Lae, Papua New Guinea",
        "Madang, Papua New Guinea",
        "Tanjung Pelepas, Malaysia",
    ],

    #PIL Shipping - converted to MELL
    "ANA Service": [
        "Lae, Papua New Guinea",
        "Motukea, Papua New Guinea",
        "Townsville, Australia",
        "Shanghai, China",
        "Ningbo, China",
        "Nansha, China",
        "Hong Kong SAR",
        "Lae, Papua New Guinea",
    ],
    "MXS Service": [
        "Hong Kong SAR",
        "Kaohsiung, Taiwan",
        "Guam",
        "Saipan, Northern Mariana Islands",
        "Yap, Micronesia",
        "Koror, Palau",
        "Hong Kong SAR",
    ],
    "EMS Service": [
        "Hong Kong SAR",
        "Kaohsiung, Taiwan",
        "Guam",
        "Chuuk, Micronesia",
        "Pohnpei, Micronesia",
        "Kosrae, Micronesia",
        "Majuro, Marshall Islands",
        "Ebeye, Marshall Islands",
        "Guam",
    ],
    "MSP Service": [
        "Lae, Papua New Guinea",
        "Honiara, Solomon Islands",
        "Suva, Fiji",
        "Lautoka, Fiji",
        "Majuro, Marshall Islands",
        "Kosrae, Micronesia",
        "Pohnpei, Micronesia",
        "Nansha, China",
        "Hong Kong SAR",
    ],

    #Kyowa Shipping
    "Saipan, Guam, Micronesia Service": [
        "Busan, South Korea",
        "Kobe, Japan",
        "Nagoya, Japan",
        "Yokohama, Japan",
        "Saipan, Northern Mariana Islands",
        "Guam",
        "Koror, Palau",
        "Yap, Micronesia",
        "Chuuk, Micronesia",
        "Pohnpei, Micronesia",
        "Kosrae, Micronesia",
        "Majuro, Marshall Islands",
        "Ebeye, Marshall Islands",
    ],
    "South Pacific Islands Service": [
        "Busan, South Korea",
        "Kobe, Japan",
        "Nagoya, Japan",
        "Yokohama, Japan",
        "Honiara, Solomon Islands",
        "Santo, Vanuatu",
        "Port Vila, Vanuatu",
        "Noumea, New Caledonia",
        "Lautoka, Fiji",
        "Suva, Fiji",
        "Nuku'alofa, Tonga",
        "Apia, Samoa",
        "Pago Pago, American Samoa",
        "Papeete, French Polynesia",
        "Tarawa, Kiribati",
    ],
    "PNG-AUS Service": [
        "Busan, South Korea",
        "Chofu, Japan",
        "Moji, Japan",
        "Kobe, Japan",
        "Nagoya, Japan",
        "Yokohama, Japan",
        "Rabaul, Papua New Guinea",
        "Lae, Papua New Guinea",
        "Motukea, Papua New Guinea",
        "Townsville, Australia",
    ],

    #Nauru Shipping
    "NSL Micronesian Pride Service": [
        "Nauru",
        "Suva, Fiji",
        "Tuvalu",
        "Nauru",
    ],
    "NSL Supplementary Service": [
        "Nauru", #all connected into one supplementary service
        "Brisbane, Australia",
        "Sydney, Australia",
        "Melbourne, Australia",
        "Nauru",
        "Auckland, New Zealand",
        "Nauru",
        "Honiara, Solomon Islands",
    ],
    #Government of Tokelau
    "Department of Transport & Support Services Service": [
        "Apia, Samoa",
        "Atafu, Tokelau",
        "Nukunonu, Tokelau",
        "Fakaofo, Tokelau",
        "Apia, Samoa",
    ],
    #Government of the Pitcairn Islands
    "MV Silver Supporter Regular Service": [
        "Mangareva, French Polynesia",
        "Pitcairn Island",
        "Mangareva, French Polynesia",
    ],
    "MV Silver Supporter NZ Freight Run Service": [
        "Mangareva, French Polynesia",
        "Auckland, New Zealand",
        "Mangareva, French Polynesia",
    ],
}

#create map for visualisation
pacific_map = folium.Map(location=[0, 180], zoom_start=3, control_scale=True, tiles="OpenStreetMap") #CartoDB positron

#add port markers for each city
for city, coords in city_coords.items():
    folium.CircleMarker(
        location=coords,
        radius=5,
        color="black",
        fill=True,
        fill_color="blue",
        fill_opacity=0.7,
        popup=f"<b>{city}</b>",
    ).add_to(pacific_map)


def offset_route(geojson, offset_distance=0.01):
    """
    offsets a GeoJSON LineString route slightly to avoid overlaps.
    :param geojson: GeoJSON object containing the route.
    :param offset_distance: Distance to offset in degrees (latitude/longitude).
    :return: New GeoJSON object with offset route.
    """
    coordinates = geojson["geometry"]["coordinates"]
    offset_coordinates = []

    for i, (lon, lat) in enumerate(coordinates):
        if i == 0:
            #use the next point to determine the offset direction
            next_lon, next_lat = coordinates[i + 1]
        else:
            #use the previous point to determine the offset direction
            prev_lon, prev_lat = coordinates[i - 1]
            next_lon, next_lat = lon, lat

        #calculate direction vector
        dx = next_lon - lon
        dy = next_lat - lat
        length = math.sqrt(dx**2 + dy**2)

        #normalise and rotate 90 degrees to calculate offset
        if length != 0:
            offset_dx = -dy / length * offset_distance
            offset_dy = dx / length * offset_distance
        else:
            offset_dx = offset_dy = 0

        #apply offset
        offset_lon = lon + offset_dx
        offset_lat = lat + offset_dy
        offset_coordinates.append([offset_lon, offset_lat])

    #create new GeoJSON with offset coordinates
    offset_geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": offset_coordinates,
        },
        "properties": geojson.get("properties", {}),
    }

    return offset_geojson

#define route as variables for each operator
#SWIRE SHIPPING
north_asia_service = [
    "Sri Racha, Thailand",
    "Kaohsiung, Taiwan",
    "Changsu, China",
    "Yokohama, Japan",
    "Osaka, Japan",
    "Busan, South Korea",
    "Lae, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Noumea, New Caledonia",
    "Auckland, New Zealand",
    "Timaru, New Zealand",
    "Tauranga, New Zealand",
    "Marsden Point, New Zealand",
    "Noumea, New Caledonia",
    "Prony Bay, New Caledonia",
    "Subic Bay, Philippines",
    "Sri Racha, Thailand",
]

pacific_islands_service = [
    "Sydney, Australia",
    "Melbourne, Australia",
    "Brisbane, Australia",
    "Prony Bay, New Caledonia",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Port Vila, Vanuatu",
    "Sydney, Australia",
]

north_asia_express = [
    "Shanghai, China",
    "Ningbo, China",
    "Nansha, China",
    "Hong Kong SAR",
    "Lae, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Townsville, Australia",
    "Shanghai, China",
]

pacific_weekly_express = [
    "Port Klang, Malaysia",
    "Singapore",
    "Jakarta, Indonesia",
    "Motukea, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Noumea, New Caledonia",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Honiara, Solomon Islands",
    "Rabaul, Papua New Guinea",
    "Madang, Papua New Guinea",
    "Port Klang, Malaysia",
]

png_service = [
    "Sydney, Australia",
    "Melbourne, Australia",
    "Brisbane, Australia",
    "Motukea, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Honiara, Solomon Islands",
    "Sydney, Australia",
]

us_west_coast_pacific_islands_service = [
    "Los Angeles, USA",
    "Oakland, USA",
    "Honolulu, Hawaii",
    "Papeete, French Polynesia",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Los Angeles, USA",
]

micronesia_service = [
    "Busan, South Korea",
    "Hakata, Japan",
    "Yokohama, Japan",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Busan, South Korea",
]

pacific_north_asia_service_loop_1 = [
    "Kaohsiung, Taiwan",
    "Tianjin, China",
    "Qingdao, China",
    "Busan, South Korea",
    "Yokohama, Japan",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Santo, Vanuatu",
    "Kaohsiung, Taiwan",
]

pacific_north_asia_service_loop_2 = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Honiara, Solomon Islands",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Tarawa, Kiribati",
    "Busan, South Korea",
]

pacific_north_asia_service_loop_3 = [
    "Busan, South Korea",
    "Majuro, Marshall Islands",
    "Tarawa, Kiribati",
    "Lae, Papua New Guinea",
    "Busan, South Korea",
]

new_zealand_eastern_pacific_service = [
    "Auckland, New Zealand",
    "Nuku'alofa, Tonga",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Rarotonga, Cook Islands",
    "Aitutaki, Cook Islands",
    "Niue",
    "Nuku'alofa, Tonga",
    "Vava'u, Tonga",
    "Auckland, New Zealand",
]

#ANL
apr_service = [
    "Port Klang, Malaysia",
    "Singapore",
    "Jakarta, Indonesia",
    "Surabaya, Indonesia",
    "Madang, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Rabaul, Papua New Guinea",
    "Kimbe, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Townsville, Australia",
    "Gladstone, Australia",
    "Port Klang, Malaysia",
]

nz_fiji_service_anl = [
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
]

pcx_service = [
    "Vancouver, Canada",
    "Oakland, USA",
    "Los Angeles, USA",
    "Auckland, New Zealand",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Adelaide, Australia",
    "Tauranga, New Zealand",
    "Seattle, USA",
    "Oakland, USA",
    "Los Angeles, USA",
    "Auckland, New Zealand",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Tauranga, New Zealand",
    "Papeete, French Polynesia",
    "Vancouver, Canada",
]

tahiti_service = [
    "Auckland, New Zealand",
    "Papeete, French Polynesia",
    "Auckland, New Zealand",
]

westpac_service = [
    "Auckland, New Zealand",
    "Noumea, New Caledonia",
    "Brisbane, Australia",
    "Townsville, Australia",
    "Motukea, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Kimbe, Papua New Guinea",
    "Rabaul, Papua New Guinea",
    "Honiara, Solomon Islands",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
]

auspac_service = [
    "Melbourne, Australia",
    "Sydney, Australia",
    "Brisbane, Australia",
    "Noumea, New Caledonia",
    "Port Vila, Vanuatu",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
    "Melbourne, Australia",
]

southpac_service = [
    "Auckland, New Zealand",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Auckland, New Zealand",
]

anz_shuttle_service = [
    "Brisbane, Australia",
    "Noumea, New Caledonia",
    "Tauranga, New Zealand",
    "Brisbane, Australia",
]

anz_wallis_futuna_service = [
    "Melbourne, Australia",
    "Sydney, Australia",
    "Brisbane, Australia",
    "Suva, Fiji",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Suva, Fiji",
]

anzpac_service = [
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
    "Tauranga, New Zealand",
]

#NPDL
nz_fiji_service_npdl = [
    "Lyttleton, New Zealand",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
]

nz_samoa_american_samoa_tonga_service = [
    "Lyttleton, New Zealand",
    "Auckland, New Zealand",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
]

nz_new_caledonia_vanuatu_service = [
    "Lyttleton, New Zealand",
    "Mount Maunganui, New Zealand",
    "Auckland, New Zealand",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
]

nz_vanuatu_service = [
    "Lyttleton, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Port Vila, Vanuatu",
    "Santo, Vanuatu",
]

nz_tahiti_service = [
    "Lyttleton, New Zealand",
    "Auckland, New Zealand",
    "Papeete, French Polynesia",
]

nz_tuvalu_wallis_futuna_kiribati_service = [
    "Lyttleton, New Zealand",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Tuvalu",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Tarawa, Kiribati",
    "Kiritimati, Kiribati",
]

nz_marshall_islands_micronesia_solomon_islands_service = [
    "Metroport, Auckland, New Zealand",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Majuro, Marshall Islands",
    "Kosrae, Micronesia",
    "Pohnpei, Micronesia",
    "Honiara, Solomon Islands",
]

nz_cook_islands_service = [
    "Auckland, New Zealand",
    "Rarotonga, Cook Islands",
    "Aitutaki, Cook Islands",
]

nz_honiara_service = [
    "Mount Maunganui, New Zealand",
    "Auckland, New Zealand",
    "Honiara, Solomon Islands",
]

aus_fiji_samoa_tonga_service = [
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
]

aus_tahiti_tonga_service = [
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Papeete, French Polynesia",
    "Nuku'alofa, Tonga",
]

aus_new_caledonia_service = [
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Noumea, New Caledonia",
]

aus_vanuatu_service = [
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
]

aus_tuvalu_wallis_futuna_kiribati_service = [
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Suva, Fiji",
    "Tuvalu",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Tarawa, Kiribati",
    "Kiritimati, Kiribati",
]

aus_solomon_islands_service = [
    "Melbourne, Australia",
    "Sydney, Australia",
    "Brisbane, Australia",
    "Honiara, Solomon Islands",
]

aus_cook_islands_service = [
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Rarotonga, Cook Islands",
    "Aitutaki, Cook Islands",
]

fj_samoa_american_samoa_tonga_nz_service = [
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
    "Tauranga, New Zealand",
    "Metroport, Auckland, New Zealand",
]

fj_aus_service = [
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Tauranga, New Zealand",
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
]

fj_vanuatu_service = [
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
]

fj_tuvalu_wallis_futuna_kiribati_service = [
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Tuvalu",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Tarawa, Kiribati",
    "Kiritimati, Kiribati",
]

fj_marshall_islands_micronesia_solomon_islands_service = [
    "Suva, Fiji",
    "Majuro, Marshall Islands",
    "Kosrae, Micronesia",
    "Pohnpei, Micronesia",
    "Honiara, Solomon Islands",
]

samoa_american_samoa_tonga_nz_aus_service = [
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
    "Tauranga, New Zealand",
    "Metroport, Auckland, New Zealand",
    "Brisbane, Australia",
    "Newcastle, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
]

new_caledonia_nz_service = [
    "Noumea, New Caledonia",
    "Suva, Fiji",
    "Tauranga, New Zealand",
]

vanuatu_nz_service = [
    "Port Vila, Vanuatu",
    "Santo, Vanuatu",
    "Suva, Fiji",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
]

new_caledonia_vanuatu_nz_service = [
    "Noumea, New Caledonia",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Auckland, New Zealand",
]

new_caledonia_wallis_futuna_vanuatu_service = [
    "Noumea, New Caledonia",
    "Suva, Fiji",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Suva, Fiji",
    "Port Vila, Vanuatu",
    "Santo, Vanuatu",
]

new_caledonia_fiji_wallis_futuna_service = [
    "Noumea, New Caledonia",
    "Suva, Fiji",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
]

calpac_us_tahiti_samoa_american_samoa_tonga_service = [
    "Long Beach, USA",
    "Oakland, USA",
    "Papeete, French Polynesia",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga",
]

calpac_us_nz_aus_service = [
    "Long Beach, USA",
    "Oakland, USA",
    "Apia, Samoa",
    "Tauranga, New Zealand",
    "Metroport, Auckland, New Zealand",
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
]

calpac_us_new_caledonia_vanuatu_service = [
    "Long Beach, USA",
    "Oakland, USA",
    "Suva, Fiji",
    "Apia, Samoa",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Port Vila, Vanuatu",
    "Santo, Vanuatu",
    "Noumea, New Caledonia",
]

calpac_tuvalu_wallis_futuna_kiribati_service = [
    "Long Beach, USA",
    "Oakland, USA",
    "Suva, Fiji",
    "Apia, Samoa",
    "Tauranga, New Zealand",
    "Suva, Fiji",
    "Tuvalu",
    "Wallis, Wallis and Futuna",
    "Futuna, Wallis and Futuna",
    "Tarawa, Kiribati",
    "Kiritimati, Kiribati",
]

calpac_aus_nz_fiji_tahiti_us_service = [
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Apia, Samoa",
    "Papeete, French Polynesia",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Long Beach, USA",
    "Oakland, USA",
]

south_pacific_service = [
    "Nansha, China",
    "Hong Kong SAR",
    "Lae, Papua New Guinea",
    "Honiara, Solomon Islands",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Tarawa, Kiribati",
    "Majuro, Marshall Islands",
    "Kosrae, Micronesia",
    "Pohnpei, Micronesia",
]

#MELL
nz_guam_saipan_micronesia = [
    "Auckland, New Zealand",
    "Lyttleton, New Zealand",
    "Wellington, New Zealand",
    "Napier, New Zealand",
    "Metroport, Auckland, New Zealand",
    "Tauranga, New Zealand",
    "Hong Kong SAR",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Yap, Micronesia",
    "Koror, Palau",
]

#Matson
matson_south_pacific_shipping = [
    "Auckland, New Zealand",
    "Nuku'alofa, Tonga",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Niue",
    "Vava'u, Tonga",
    "Nuku'alofa, Tonga",
    "Vava'u, Tonga", #added later to fix
    "Niue", 
    "Pago Pago, American Samoa", 
    "Rarotonga, Cook Islands",
    "Aitutaki, Cook Islands",
    "Nuku'alofa, Tonga",
    "Lautoka, Fiji",
    "Brisbane, Australia",
    "Sydney, Australia", 
    "Melbourne, Australia", 
    "Lautoka, Fiji",
    "Sydney, Australia", 
    "Lautoka, Fiji",
    "Melbourne, Australia",
]

matson_guam_and_micronesia_shipping_service = [
    "Long Beach, USA",
    "Shanghai, China",
    "Ningbo, China",
    "Okinawa, Japan",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Tinian, Northern Mariana Islands",
    "Chuuk, Micronesia",
    "Pohnpei, Micronesia",
    "Kosrae, Micronesia",
    "Majuro, Marshall Islands",
    "Ebeye, Marshall Islands",
    "Kwajalein, Marshall Islands",
    "Honolulu, Hawaii",
]

#MAERSK
fiji_express_service = [
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Tauranga, New Zealand",
]

png_express_service = [
    "Tanjung Pelepas, Malaysia",
    "Motukea, Papua New Guinea",
    "Noro, Solomon Islands",
    "Lae, Papua New Guinea",
    "Madang, Papua New Guinea",
]

# PIL Shipping
ana_service = [
    "Lae, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Townsville, Australia",
    "Shanghai, China",
    "Ningbo, China",
    "Nansha, China",
    "Hong Kong SAR",
]

mxs_service = [
    "Hong Kong SAR",
    "Kaohsiung, Taiwan",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Yap, Micronesia",
    "Koror, Palau",
]

ems_service = [
    "Hong Kong SAR",
    "Kaohsiung, Taiwan",
    "Guam",
    "Chuuk, Micronesia",
    "Pohnpei, Micronesia",
    "Kosrae, Micronesia",
    "Majuro, Marshall Islands",
    "Ebeye, Marshall Islands",
]

msp_service = [
    "Lae, Papua New Guinea",
    "Honiara, Solomon Islands",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Majuro, Marshall Islands",
    "Kosrae, Micronesia",
    "Pohnpei, Micronesia",
    "Nansha, China",
    "Hong Kong SAR",
]


#PIL - converted to MELL
ana_service = [
    "Lae, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Townsville, Australia",
    "Shanghai, China",
    "Ningbo, China",
    "Nansha, China",
    "Hong Kong SAR",
    "Lae, Papua New Guinea",
]

mxs_service = [
    "Hong Kong SAR",
    "Kaohsiung, Taiwan",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Yap, Micronesia",
    "Koror, Palau",
]

ems_service = [
    "Hong Kong SAR",
    "Kaohsiung, Taiwan",
    "Guam",
    "Chuuk, Micronesia",
    "Pohnpei, Micronesia",
    "Kosrae, Micronesia",
    "Majuro, Marshall Islands",
    "Ebeye, Marshall Islands",
]

msp_service = [
    "Lae, Papua New Guinea",
    "Honiara, Solomon Islands",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Majuro, Marshall Islands",
    "Kosrae, Micronesia",
    "Pohnpei, Micronesia",
    "Nansha, China",
    "Hong Kong SAR",
]


#Kyowa Shipping
saipan_guam_micronesia_service = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Saipan, Northern Mariana Islands",
    "Guam",
    "Koror, Palau",
    "Yap, Micronesia",
    "Chuuk, Micronesia",
    "Pohnpei, Micronesia",
    "Kosrae, Micronesia",
    "Majuro, Marshall Islands",
    "Ebeye, Marshall Islands",
]

south_pacific_islands_service = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Honiara, Solomon Islands",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Tarawa, Kiribati",
]

png_aus_service = [
    "Busan, South Korea",
    "Chofu, Japan",
    "Moji, Japan",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Rabaul, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Townsville, Australia",
]

#Nauru Shipping Line
nsl_micronesian_pride_service = [
    "Nauru",
    "Suva, Fiji",
    "Tuvalu",
    "Nauru",
]

nsl_supplementary_service = [
    "Nauru",
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Honiara, Solomon Islands",
]

#Government of Tokelau
department_transport_tokelau = [
    "Apia, Samoa",
    "Atafu, Tokelau",
    "Nukunonu, Tokelau",
    "Fakaofo, Tokelau",
    "Apia, Samoa",
]

#Government of the Pitcairn Islands
mv_silver_supporter_regular = [
    "Mangareva, French Polynesia",
    "Pitcairn Island",
    "Mangareva, French Polynesia",
]

mv_silver_supporter_nz_freight_run_service = [
    "Mangareva, French Polynesia",
    "Auckland, New Zealand",
]

#branches that needed splitting for better visualisation
# US West Coast - Pacific Islands Service
us_west_coast_pacific_islands_us_branch_1 = [
    "Long Beach, USA",
    "Oakland, USA",
    "Papeete, French Polynesia",
]

us_west_coast_pacific_islands_us_branch_2 = [
    "Pago Pago, American Samoa",
    "Long Beach, USA",
]

us_west_coast_pacific_islands_pacific_branch = [
    "Papeete, French Polynesia",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
]

us_west_coast_pacific_islands_pacific_branch_line = [
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Apia, Samoa",
]
#define US West Coast - Pacific Extra Branches as sea-routed services
us_west_coast_pacific_extra_branch_1 = [
    "Apia, Samoa",
    "Melbourne, Australia",
    "Sydney, Australia",
    "Brisbane, Australia",
    "Port Vila, Vanuatu",
]

us_west_coast_pacific_extra_branch_2 = [
    "Apia, Samoa",
    "Noumea, New Caledonia",
    "Santo, Vanuatu",
]

us_west_coast_pacific_extra_branch_3 = [
    "Apia, Samoa",
    "Rarotonga, Cook Islands",
    "Aitutaki, Cook Islands",
    "Niue",
    "Vava'u, Tonga",
    "Nuku'alofa, Tonga",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Lautoka, Fiji",
    "Nuku'alofa, Tonga",
    "Auckland, New Zealand",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Nelson, New Zealand",
    "Auckland, New Zealand",
    "Napier, New Zealand",
    "Auckland, New Zealand",
    "Lyttleton, New Zealand",
    "Auckland, New Zealand",
    "Timaru, New Zealand",
    "Auckland, New Zealand",
]

# PCX Service
pcx_us_branch_1 = [
    "Vancouver, Canada",
    "Oakland, USA",
    "Los Angeles, USA",
    "Auckland, New Zealand",
]

pcx_us_branch_2 = [
    "Tauranga, New Zealand",
    "Seattle, USA",
    "Oakland, USA",
    "Los Angeles, USA",
    "Auckland, New Zealand",
]

pcx_us_branch_3 = [
    "Papeete, French Polynesia",
    "Vancouver, Canada",
]

pcx_pacific_branch_1 = [
    "Auckland, New Zealand",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Adelaide, Australia",
    "Tauranga, New Zealand",
]

pcx_pacific_branch_2 = [
    "Auckland, New Zealand",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Tauranga, New Zealand",
    "Papeete, French Polynesia",
]

matson_guam_micronesia_us_branch_1 = [
    "Long Beach, USA",
    "Shanghai, China",
]

matson_guam_micronesia_pacific_branch_1 = [
    "Shanghai, China",
    "Ningbo, China",
    "Okinawa, Japan",
    "Guam",
    "Saipan, Northern Mariana Islands",
    "Tinian, Northern Mariana Islands",
    "Saipan, Northern Mariana Islands",
    "Guam",
    "Honolulu, Hawaii",
]

matson_guam_micronesia_us_branch_2 = [
    "Honolulu, Hawaii",
    "Oakland, USA",
    "Long Beach, USA",
    "Honolulu, Hawaii",
    "Long Beach, USA",
    "Honolulu, Hawaii",
    "Tacoma, USA",
    "Oakland, USA",
    "Honolulu, Hawaii",
]

matson_guam_micronesia_pacific_branch_2 = [
    "Honolulu, Hawaii",
    "Guam",
    "Yap, Micronesia",
    "Koror, Palau",
    "Yap, Micronesia",
    "Guam",
    "Chuuk, Micronesia",
    "Pohnpei, Micronesia",
    "Kosrae, Micronesia",
    "Majuro, Marshall Islands",
    "Ebeye, Marshall Islands",
    "Kwajalein, Marshall Islands",
    "Guam",
]

#define PNG Service - Extra Branches as sea-routed services
png_service_extra_branch_1 = [
    "Lae, Papua New Guinea",
    "Madang, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Wewak, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Kavieng, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Rabaul, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Buka, Papua New Guinea",
    "Lae, Papua New Guinea",
    "Kimbe, Papua New Guinea",
]

png_service_extra_branch_2 = [
    "Motukea, Papua New Guinea",
    "Oro Bay, Papua New Guinea",
    "Motukea, Papua New Guinea",
    "Alotau, Papua New Guinea",
]

png_service_extra_branch_3 = [
    "Townsville, Australia",
    "Brisbane, Australia",
]

png_service_extra_branch_4 = [
    "Melbourne, Australia",
    "Adelaide, Australia",
    "Melbourne, Australia",
    "Fremantle, Australia",
]

#define NZ Eastern Pacific - Extra Branches as sea-routed services
nz_eastern_pacific_extra_branch_1 = [
    "Auckland, New Zealand",
    "Tauranga, New Zealand",
    "Auckland, New Zealand",
    "Napier, New Zealand",
    "Auckland, New Zealand",
    "Nelson, New Zealand",
    "Auckland, New Zealand",
    "Lyttleton, New Zealand",
    "Auckland, New Zealand",
    "Timaru, New Zealand",
]

nz_eastern_pacific_extra_branch_2 = [
    "Apia, Samoa",
    "Papeete, French Polynesia",
]

nz_eastern_pacific_extra_branch_3 = [
    "Suva, Fiji",
    "Nauru",
]

#define Swire Pacific - Extra Branch 1
swire_pacific_extra_branch_1 = [
    "Suva, Fiji",
    "Nauru",
    "Suva, Fiji",
    "Tuvalu",
    "Suva, Fiji",
    "Papeete, French Polynesia",
    "Suva, Fiji",
    "Apia, Samoa",
    "Suva, Fiji",
    "Pago Pago, American Samoa",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
]

#define Swire Pacific - Extra Branch 2
swire_pacific_extra_branch_2 = [
    "Port Vila, Vanuatu",
    "Santo, Vanuatu",
]

#new services added later
nyk_south_pacific_link = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Honiara, Solomon Islands",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Tarawa, Kiribati",
    "Papeete, French Polynesia",
    "Pago Pago, American Samoa",
    "Apia, Samoa",
    "Nuku'alofa, Tonga",
    "Busan, South Korea",
]

cma_pad_service = [
    "Papeete, French Polynesia",
    "Noumea, New Caledonia",
    "Brisbane, Australia",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Tauranga, New Zealand",
    "Manzanillo, Panama",
]

cma_pad_service_usbranch = [
    "Manzanillo, Panama",
    "Savannah, USA",
    "Kingston, Jamaica",
    "Papeete, French Polynesia",
]

one_south_pacific_service_loop_a = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Honiara, Solomon Islands",
    "Santo, Vanuatu",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Busan, South Korea",
]

one_south_pacific_service_loop_b = [
    "Busan, South Korea",
    "Kobe, Japan",
    "Nagoya, Japan",
    "Yokohama, Japan",
    "Honiara, Solomon Islands",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Papeete, French Polynesia",
    "Tarawa, Kiribati",
    "Busan, South Korea",
]

one_south_pacific_service_loop_c = [
    "Kaohsiung, Taiwan",
    "Xingang, China",
    "Qingdao, China",
    "Busan, South Korea",
    "Yokohama, Japan",
    "Tarawa, Kiribati",
    "Port Vila, Vanuatu",
    "Noumea, New Caledonia",
    "Lautoka, Fiji",
    "Suva, Fiji",
    "Nuku'alofa, Tonga",
    "Apia, Samoa",
    "Pago Pago, American Samoa",
    "Santo, Vanuatu",
    "Kaohsiung, Taiwan",
]

carpenters_kyowa = [
    "Kaohsiung, Taiwan", "Xingang, China", "Qingdao, China", "Shanghai, China",
    "Busan, South Korea", "Kobe, Japan", "Yokohama, Japan", "Majuro, Marshall Islands",
    "Tarawa, Kiribati", "Honiara, Solomon Islands", "Santo, Vanuatu", "Port Vila, Vanuatu",
    "Noumea, New Caledonia", "Lautoka, Fiji", "Suva, Fiji", "Nuku'alofa, Tonga",
    "Apia, Samoa", "Pago Pago, American Samoa", "Papeete, French Polynesia", 
    "Tarawa, Kiribati", "Noumea, New Caledonia", "Santo, Vanuatu", "Kaohsiung, Taiwan",
]

carpenters_one = [
    "Shanghai, China", "Kaohsiung, Taiwan", "Xingang, China", "Qingdao, China",
    "Busan, South Korea", "Kobe, Japan", "Nagoya, Japan", "Yokohama, Japan",
    "Majuro, Marshall Islands", "Tarawa, Kiribati", "Honiara, Solomon Islands",
    "Santo, Vanuatu", "Port Vila, Vanuatu", "Noumea, New Caledonia", "Lautoka, Fiji",
    "Suva, Fiji", "Nuku'alofa, Tonga", "Apia, Samoa", "Pago Pago, American Samoa",
    "Papeete, French Polynesia", "Nuku'alofa, Tonga", "Tarawa, Kiribati",
    "Shanghai, China", "Santo, Vanuatu",
]

msc_noumea_express = [
    "Sydney, Australia", "Brisbane, Australia", "Noumea, New Caledonia",
    "Lautoka, Fiji", "Suva, Fiji", "Sydney, Australia",
]

msc_oceania_loop_1 = [
    "Sydney, Australia", "Melbourne, Australia", "Adelaide, Australia", 
    "Tauranga, New Zealand",
]

msc_oceania_loop_1_usbranch = [
    "Tauranga, New Zealand", "Oakland, USA", "Seattle, USA", "Vancouver, Canada", 
    "Long Beach, USA",
]

msc_oceania_loop_2 = [
    "Sydney, Australia", "Melbourne, Australia", "Tauranga, New Zealand", 
    "Papeete, French Polynesia",
]

msc_oceania_loop_2_usbranch = [
    "Papeete, French Polynesia", "Oakland, USA", "Long Beach, USA",
]

pfl_nz_east_pacific = [
    "Lyttleton, New Zealand", "Nelson, New Zealand", "Napier, New Zealand",
    "Tauranga, New Zealand", "Auckland, New Zealand", "Suva, Fiji", "Lautoka, Fiji",
    "Apia, Samoa", "Pago Pago, American Samoa", "Nuku'alofa, Tonga", 
    "Papeete, French Polynesia", "Rarotonga, Cook Islands", "Aitutaki, Cook Islands",
]

pfl_nz_westnorth_pacific = [
    "Lyttleton, New Zealand", "Nelson, New Zealand", "Napier, New Zealand",
    "Tauranga, New Zealand", "Auckland, New Zealand", "Noumea, New Caledonia",
    "Suva, Fiji", "Lautoka, Fiji", "Motukea, Papua New Guinea", "Lae, Papua New Guinea",
]

pfl_aus_eastwest_pacific = [
    "Newcastle, Australia", "Sydney, Australia", "Melbourne, Australia",
    "Brisbane, Australia", "Noumea, New Caledonia", "Lautoka, Fiji", "Suva, Fiji",
    "Motukea, Papua New Guinea", "Lae, Papua New Guinea", "Motukea, Papua New Guinea",
    "Suva, Fiji", "Apia, Samoa", "Pago Pago, American Samoa", "Nuku'alofa, Tonga",
]

pfl_aus_tahiti = [
    "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia",
    "Auckland, New Zealand", "Papeete, French Polynesia", "Auckland, New Zealand",
    "Rarotonga, Cook Islands", "Aitutaki, Cook Islands",
]

pfl_lcl_schedule_1 = [
    "Auckland, New Zealand", "Apia, Samoa", "Pago Pago, American Samoa", 
    "Nuku'alofa, Tonga",
]

pfl_lcl_schedule_2 = [
    "Auckland, New Zealand", "Suva, Fiji", "Lautoka, Fiji",
]

pfl_islands_schedule = [
    "Apia, Samoa", "Pago Pago, American Samoa", "Nuku'alofa, Tonga",
    "Tauranga, New Zealand", "Auckland, New Zealand", "Tauranga, New Zealand",
    "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia",
]

pfl_fiji_schedule = [
    "Suva, Fiji", "Lautoka, Fiji", "Apia, Samoa", "Pago Pago, American Samoa",
    "Nuku'alofa, Tonga", "Tauranga, New Zealand", "Auckland, New Zealand",
    "Newcastle, Australia", "Sydney, Australia", "Melbourne, Australia",
    "Brisbane, Australia",
]

#--------------------------------------------------------------------------------------------------------

#snapping function to lock onto port
def snap_to_city_marker(route_geojson, start_coords, end_coords):
    """
    Adjust the GeoJSON route's start and end coordinates to exactly match the city markers.
    """
    route_geojson["geometry"]["coordinates"][0] = list(start_coords)
    route_geojson["geometry"]["coordinates"][-1] = list(end_coords)
    return route_geojson

#route offset
def offset_route(route_geojson, offset_distance=0.01):
    """
    Offset the route by modifying its coordinates slightly to avoid overlap.
    """
    offset_coords = []
    for index, (lon, lat) in enumerate(route_geojson["geometry"]["coordinates"]):
        # Alternate the offset direction to avoid uniform shifts
        direction = 1 if index % 2 == 0 else -1
        offset_coords.append([lon + (offset_distance * direction), lat + (offset_distance * direction)])
    
    # Replace original coordinates with offset ones
    route_geojson["geometry"]["coordinates"] = offset_coords
    return route_geojson

#adding routes to map
def add_service_to_map(service_name, service_route, operator, offset=False, offset_distance=0.01, route_index=0):
    """
    add a shipping service route to the map, applying dynamic offsets if needed.
    
    Args:
    - service_name: Name of the service.
    - service_route: List of ports in the route.
    - operator: Name of the operator.
    - offset: Whether to apply an offset to the route.
    - offset_distance: Base offset distance.
    - route_index: An index to vary the offset per route.
    """
    color = operator_colors[operator]
    service_layer = folium.FeatureGroup(name=service_name, overlay=True)

    for i in range(len(service_route) - 1):
        start_port = service_route[i]
        end_port = service_route[i + 1]

        try:
            #retrieve coordinates for the start and end ports
            start_coords = searoute_coords[start_port]
            end_coords = searoute_coords[end_port]

            #generate the realistic sea route
            route = sr.searoute(start_coords, end_coords)

            #snap the route to the city markers
            route = snap_to_city_marker(route, start_coords, end_coords)

            #apply dynamic offset if needed
            if offset:
                #dynamically vary the offset based on the route index and leg index
                dynamic_offset = offset_distance * ((route_index % 3) + 1) * ((i % 2) * 2 - 1)
                route = offset_route(route, dynamic_offset)

            #add the route to the service layer
            folium.GeoJson(
                route,
                style_function=lambda x, clr=color: {
                    "color": clr,
                    "weight": 2,
                    "opacity": 0.8,
                },
            ).add_to(service_layer)

        except Exception as e:
            print(f"Failed to calculate route between {start_port} and {end_port}: {e}")
    
    #add the completed service layer to the map
    service_layer.add_to(pacific_map)


def add_mixed_service_to_map(service_name, service_route, operator, offset=False, offset_distance=0.01, route_index=0, problematic_ports=None):
    """
    add a shipping service route to the map with a mix of straight-line and realistic sea routes.
    
    Args:
    - service_name: Name of the service.
    - service_route: List of ports in the route.
    - operator: Name of the operator.
    - offset: Whether to apply an offset to the route.
    - offset_distance: Base offset distance.
    - route_index: An index to vary the offset per route.
    - problematic_ports: List of ports that require straight-line routes.
    """
    color = operator_colors[operator]
    service_layer = folium.FeatureGroup(name=service_name, overlay=True)
    problematic_ports = problematic_ports or []  #default to empty list if not provided

    for i in range(len(service_route) - 1):
        start_port = service_route[i]
        end_port = service_route[i + 1]

        try:
            #retrieve coordinates for the start and end ports
            start_coords = searoute_coords[start_port]
            end_coords = searoute_coords[end_port]

            #check if either port is in the problematic ports list
            if start_port in problematic_ports or end_port in problematic_ports:
                #create a straight-line route
                route = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [start_coords, end_coords],
                    },
                }
            else:
                #generate the realistic sea route
                route = sr.searoute(start_coords, end_coords)
                #snap the route to the city markers
                route = snap_to_city_marker(route, start_coords, end_coords)

            #apply dynamic offset if needed
            if offset:
                dynamic_offset = offset_distance * ((route_index % 3) + 1) * ((i % 2) * 2 - 1)
                route = offset_route(route, dynamic_offset)

            #add the route to the service layer
            folium.GeoJson(
                route,
                style_function=lambda x, clr=color: {
                    "color": clr,
                    "weight": 2,
                    "opacity": 0.8,
                },
            ).add_to(service_layer)

        except Exception as e:
            print(f"Failed to calculate route between {start_port} and {end_port}: {e}")

    #add the completed service layer to the map
    service_layer.add_to(pacific_map)


def add_straight_line_service_to_map(service_name, service_route, operator, offset=False, offset_distance=0.01):
    """
    add a straight-line shipping service route to the map, with optional offsets.
    
    Args:
    - service_name: Name of the service.
    - service_route: List of ports in the route.
    - operator: Name of the operator.
    - offset: Whether to apply an offset to the route.
    - offset_distance: Offset distance to apply if offset is enabled.
    """
    color = operator_colors[operator]
    service_layer = folium.FeatureGroup(name=service_name, overlay=True)

    for i in range(len(service_route) - 1):
        start_port = service_route[i]
        end_port = service_route[i + 1]

        try:
            #retrieve coordinates for the start and end ports
            start_coords = searoute_coords[start_port]
            end_coords = searoute_coords[end_port]

            #apply offset to coordinates if enabled
            if offset:
                start_coords = (start_coords[0] + offset_distance, start_coords[1] + offset_distance)
                end_coords = (end_coords[0] + offset_distance, end_coords[1] + offset_distance)

            #create a straight-line GeoJSON object
            route_geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [start_coords, end_coords],
                },
            }

            #add the straight-line route to the service layer
            folium.GeoJson(
                route_geojson,
                style_function=lambda x, clr=color: {
                    "color": clr,
                    "weight": 2,
                    "opacity": 0.8,
                },
            ).add_to(service_layer)

        except Exception as e:
            print(f"Failed to calculate straight line between {start_port} and {end_port}: {e}")
    
    #add the completed service layer to the map
    service_layer.add_to(pacific_map)


#add individual services ---------------------------------------------------------------------------------------------------------

#SWIRE Shipping
add_service_to_map("North Asia Service", north_asia_service, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("Pacific Islands Service", pacific_islands_service, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("North Asia Express", north_asia_express, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("Pacific Weekly Express", pacific_weekly_express, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("PNG Service", png_service, "Swire Shipping", offset=True, offset_distance=0.01)

#add_service_to_map("US West Coast - Pacific Islands Service", us_west_coast_pacific_islands_service, "Swire Shipping")  #temporarily removed for consistency

add_service_to_map("Micronesia Service", micronesia_service, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("Pacific North Asia Service - Loop 1", pacific_north_asia_service_loop_1, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("Pacific North Asia Service - Loop 2", pacific_north_asia_service_loop_2, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("Pacific North Asia Service - Loop 3", pacific_north_asia_service_loop_3, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("New Zealand Eastern Pacific Service", new_zealand_eastern_pacific_service, "Swire Shipping", offset=True, offset_distance=0.01)

#ANL
add_service_to_map("APR Service", apr_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("NZ-Fiji Service ANL", nz_fiji_service_anl, "ANL", offset=True, offset_distance=0.015)

#add_service_to_map("PCX Service", pcx_service, "ANL") #temporarily removed for consistency

add_service_to_map("Tahiti Service", tahiti_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("WESTPAC Service", westpac_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("AUSPAC Service", auspac_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("SOUTHPAC Service", southpac_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("ANZ Shuttle Service", anz_shuttle_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("ANZ Wallis-Futuna Service", anz_wallis_futuna_service, "ANL", offset=True, offset_distance=0.015)
add_service_to_map("ANZPAC Service", anzpac_service, "ANL", offset=True, offset_distance=0.015)

#NPDL
add_service_to_map("NZ-Fiji Service NPDL", nz_fiji_service_npdl, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Samoa, American Samoa, Tonga Service", nz_samoa_american_samoa_tonga_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-New Caledonia, Vanuatu Service", nz_new_caledonia_vanuatu_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Vanuatu Service", nz_vanuatu_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Tahiti Service", nz_tahiti_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Tuvalu, Wallis and Futuna, Kiribati Service", nz_tuvalu_wallis_futuna_kiribati_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Marshall Islands, Micronesia, Solomon Islands Service", nz_marshall_islands_micronesia_solomon_islands_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Cook Islands Service", nz_cook_islands_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("NZ-Honiara Service", nz_honiara_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Fiji, Samoa, Tonga Service", aus_fiji_samoa_tonga_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Tahiti, Tonga Service", aus_tahiti_tonga_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-New Caledonia Service", aus_new_caledonia_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Vanuatu Service", aus_vanuatu_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Tuvalu, Wallis and Futuna, Kiribati Service", aus_tuvalu_wallis_futuna_kiribati_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Solomon Islands Service", aus_solomon_islands_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("AUS-Cook Islands Service", aus_cook_islands_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("FJ-Samoa, American Samoa, Tonga, NZ Service", fj_samoa_american_samoa_tonga_nz_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("FJ-AUS Service", fj_aus_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("FJ-Vanuatu Service", fj_vanuatu_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("FJ-Tuvalu, Wallis and Futuna, Kiribati Service", fj_tuvalu_wallis_futuna_kiribati_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("FJ-Marshall Islands, Micronesia, Solomon Islands Service", fj_marshall_islands_micronesia_solomon_islands_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("Samoa, American Samoa, Tonga-NZ, AUS Service", samoa_american_samoa_tonga_nz_aus_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("New Caledonia-NZ Service", new_caledonia_nz_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("Vanuatu-NZ Service", vanuatu_nz_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("New Caledonia, Vanuatu-NZ Service", new_caledonia_vanuatu_nz_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("New Caledonia-Wallis and Futuna, Vanuatu Service", new_caledonia_wallis_futuna_vanuatu_service, "NPDL", offset=True, offset_distance=0.02)
add_service_to_map("New Caledonia-Fiji, Wallis and Futuna Service", new_caledonia_fiji_wallis_futuna_service, "NPDL", offset=True, offset_distance=0.02)

#temporarily removed for consistency
#add_service_to_map("CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service", calpac_us_tahiti_samoa_american_samoa_tonga_service, "NPDL", offset=True, offset_distance=0.01, route_index=1)
#add_service_to_map("CALPAC US-NZ, AUS Service", calpac_us_nz_aus_service, "NPDL", offset=True, offset_distance=0.01, route_index=2)
#add_service_to_map("CALPAC US-New Caledonia, Vanuatu Service", calpac_us_new_caledonia_vanuatu_service, "NPDL", offset=True, offset_distance=0.01, route_index=3)
#add_service_to_map("CALPAC Tuvalu, Wallis and Futuna, Kiribati Service", calpac_tuvalu_wallis_futuna_kiribati_service, "NPDL", offset=True, offset_distance=0.01, route_index=4)
#add_service_to_map("CALPAC AUS, NZ, Fiji, Tahiti-US Service", calpac_aus_nz_fiji_tahiti_us_service, "NPDL", offset=True, offset_distance=0.01, route_index=5)

add_service_to_map("South Pacific Service", south_pacific_service, "NPDL", offset=True, offset_distance=0.02)

#MELL
add_service_to_map("NZ-Guam, Saipan, Micronesia", nz_guam_saipan_micronesia, "MELL", offset=True, offset_distance=0.03)

#Matson
add_service_to_map("Matson South Pacific Shipping Service", matson_south_pacific_shipping, "Matson", offset=True, offset_distance=0.03)

#MAERSK
add_service_to_map("Fiji Express Service", fiji_express_service, "MAERSK", offset=True, offset_distance=0.03)
add_service_to_map("PNG Express Service", png_express_service, "MAERSK", offset=True, offset_distance=0.03)

#PIL converted to MELL
add_service_to_map("ANA Service", ana_service, "MELL", offset=True, offset_distance=0.03)
add_service_to_map("MXS Service", mxs_service, "MELL", offset=True, offset_distance=0.03)
add_service_to_map("EMS Service", ems_service, "MELL", offset=True, offset_distance=0.03)
add_service_to_map("MSP Service", msp_service, "MELL", offset=True, offset_distance=0.03)

#Kyowa Shipping
add_service_to_map("Saipan, Guam, Micronesia Service", saipan_guam_micronesia_service, "Kyowa Shipping", offset=True, offset_distance=0.03)
add_service_to_map("South Pacific Islands Service", south_pacific_islands_service, "Kyowa Shipping", offset=True, offset_distance=0.03)
add_service_to_map("PNG-AUS Service", png_aus_service, "Kyowa Shipping", offset=True, offset_distance=0.03)

#Nauru Shipping Line
add_service_to_map("NSL Micronesian Pride Service", nsl_micronesian_pride_service, "Nauru Shipping Line", offset=True, offset_distance=0.03)
add_service_to_map("NSL Supplementary Service", nsl_supplementary_service, "Nauru Shipping Line", offset=True, offset_distance=0.03)

#Government of Tokelau - made straight line
#add_service_to_map("Department of Transport & Support Services Service", department_transport_tokelau, "Government of Tokelau", offset=True, offset_distance=0.03)
add_straight_line_service_to_map(
    "Department of Transport & Support Services Service", 
    department_transport_tokelau, 
    "Government of Tokelau", 
    offset=True, 
    offset_distance=0.03
)

#Government of the Pitcairn Islands
add_service_to_map("MV Silver Supporter Regular Service", mv_silver_supporter_regular, "Government of the Pitcairn Islands", offset=True, offset_distance=0.03)
add_service_to_map("MV Silver Supporter NZ Freight Run Service", mv_silver_supporter_nz_freight_run_service, "Government of the Pitcairn Islands", offset=True, offset_distance=0.03)

#routes with issues - mixed straight and searoute
#problematic ports for searoute mapping
us_ports = ["Long Beach, USA", "Oakland, USA"]

#use the mixed function for routes involving US ports
#add_mixed_service_to_map("US West Coast - Pacific Islands Service", us_west_coast_pacific_islands_service, "Swire Shipping", offset=True, offset_distance=0.01, route_index=1, problematic_ports=us_ports)
#add_mixed_service_to_map("PCX Service", pcx_service, "ANL", offset=True, offset_distance=0.01, route_index=2, problematic_ports=us_ports)
add_mixed_service_to_map("CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service", calpac_us_tahiti_samoa_american_samoa_tonga_service, "NPDL", offset=True, offset_distance=0.01, route_index=3, problematic_ports=us_ports)
add_mixed_service_to_map("CALPAC US-NZ, AUS Service", calpac_us_nz_aus_service, "NPDL", offset=True, offset_distance=0.01, route_index=4, problematic_ports=us_ports)
add_mixed_service_to_map("CALPAC US-New Caledonia, Vanuatu Service", calpac_us_new_caledonia_vanuatu_service, "NPDL", offset=True, offset_distance=0.01, route_index=5, problematic_ports=us_ports)
add_mixed_service_to_map("CALPAC Tuvalu, Wallis and Futuna, Kiribati Service", calpac_tuvalu_wallis_futuna_kiribati_service, "NPDL", offset=True, offset_distance=0.01, route_index=6, problematic_ports=us_ports)
add_mixed_service_to_map("CALPAC AUS, NZ, Fiji, Tahiti-US Service", calpac_aus_nz_fiji_tahiti_us_service, "NPDL", offset=True, offset_distance=0.01, route_index=7, problematic_ports=us_ports)

#ADD split services (west coast and PCX)
#US West Coast - Pacific Islands Service
add_straight_line_service_to_map(
    "US West Coast - Pacific Islands Service (US Branch 1)", 
    us_west_coast_pacific_islands_us_branch_1, 
    "Swire Shipping", 
    offset=True, 
    offset_distance=0.02
)

add_straight_line_service_to_map(
    "US West Coast - Pacific Islands Service (US Branch 2)", 
    us_west_coast_pacific_islands_us_branch_2, 
    "Swire Shipping", 
    offset=True, 
    offset_distance=0.02
)


add_service_to_map(
    "US West Coast - Pacific Islands Service (Pacific Branch)",
    us_west_coast_pacific_islands_pacific_branch,
    "Swire Shipping",
    offset=True,
    offset_distance=0.01,
    route_index=1
)

add_straight_line_service_to_map(
    "US West Coast - Pacific Islands Service (Apia-Pago Pago Connection)", 
    us_west_coast_pacific_islands_pacific_branch_line, 
    "Swire Shipping", 
    offset=True, 
    offset_distance=0.02
) #extra little fix to reflect connection between apia and pago pago

#add the new branches to the map
add_service_to_map("US West Coast - Pacific Extra Branch 1", us_west_coast_pacific_extra_branch_1, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("US West Coast - Pacific Extra Branch 2", us_west_coast_pacific_extra_branch_2, "Swire Shipping", offset=True, offset_distance=0.02)
add_service_to_map("US West Coast - Pacific Extra Branch 3", us_west_coast_pacific_extra_branch_3, "Swire Shipping", offset=True, offset_distance=0.03)


#PCX Service
add_straight_line_service_to_map(
    "PCX Service (US Branch 1)",
    pcx_us_branch_1,
    "ANL"
)

add_straight_line_service_to_map(
    "PCX Service (US Branch 2)",
    pcx_us_branch_2,
    "ANL"
)

add_straight_line_service_to_map(
    "PCX Service (US Branch 3)",
    pcx_us_branch_3,
    "ANL"
)

add_service_to_map(
    "PCX Service (Pacific Branch 1)",
    pcx_pacific_branch_1,
    "ANL",
    offset=True,
    offset_distance=0.01,
    route_index=2
)

add_service_to_map(
    "PCX Service (Pacific Branch 2)",
    pcx_pacific_branch_2,
    "ANL",
    offset=True,
    offset_distance=0.01,
    route_index=3
)

add_straight_line_service_to_map(
    "Matson Guam and Micronesia (US Branch 1)",
    matson_guam_micronesia_us_branch_1,
    "Matson",
    offset=True,
    offset_distance=0.02,
)

add_straight_line_service_to_map(
    "Matson Guam and Micronesia (US Branch 2)",
    matson_guam_micronesia_us_branch_2,
    "Matson",
    offset=True,
    offset_distance=0.02,
)

add_service_to_map(
    "Matson Guam and Micronesia (Pacific Branch 1)",
    matson_guam_micronesia_pacific_branch_1,
    "Matson",
    offset=True,
    offset_distance=0.02,
    route_index=8,
)

add_service_to_map(
    "Matson Guam and Micronesia (Pacific Branch 2)",
    matson_guam_micronesia_pacific_branch_2,
    "Matson",
    offset=True,
    offset_distance=0.02,
    route_index=9,
)

#add the PNG service branches to the map
add_service_to_map("PNG Service Extra Branch 1", png_service_extra_branch_1, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("PNG Service Extra Branch 2", png_service_extra_branch_2, "Swire Shipping", offset=True, offset_distance=0.02)
add_service_to_map("PNG Service Extra Branch 3", png_service_extra_branch_3, "Swire Shipping", offset=True, offset_distance=0.03)
add_service_to_map("PNG Service Extra Branch 4", png_service_extra_branch_4, "Swire Shipping", offset=True, offset_distance=0.04)

#add the NZ eastern pacific branches to the map
add_service_to_map("NZ Eastern Pacific Extra Branch 1", nz_eastern_pacific_extra_branch_1, "Swire Shipping", offset=True, offset_distance=0.01)
add_service_to_map("NZ Eastern Pacific Extra Branch 2", nz_eastern_pacific_extra_branch_2, "Swire Shipping", offset=True, offset_distance=0.02)
add_service_to_map("NZ Eastern Pacific Extra Branch 3", nz_eastern_pacific_extra_branch_3, "Swire Shipping", offset=True, offset_distance=0.03)

#add the Swire Pacific Extra Branch 1 route to the map
add_service_to_map(
    "Swire Pacific Extra Branch 1",
    swire_pacific_extra_branch_1,
    "Swire Shipping",
    offset=True,
    offset_distance=0.01
)

#add the Swire Pacific Extra Branch 2 route to the map
add_service_to_map(
    "Swire Pacific Extra Branch 2",
    swire_pacific_extra_branch_2,
    "Swire Shipping",
    offset=True,
    offset_distance=0.01
)

#new services

add_service_to_map("CMA CGM PAD Service", cma_pad_service, "CMA CGM", offset=True, offset_distance=0.045)
add_service_to_map("NYK South Pacific Link", nyk_south_pacific_link, "NYK", offset=True, offset_distance=0.035)

add_straight_line_service_to_map("CMA CGM PAD Service - US Branch", cma_pad_service_usbranch, "CMA CGM", offset=True, offset_distance=0.045)

add_service_to_map("ONE South Pacific Service Loop A", one_south_pacific_service_loop_a, "ONE", offset=True, offset_distance=0.05)
add_service_to_map("ONE South Pacific Service Loop B", one_south_pacific_service_loop_b, "ONE", offset=True, offset_distance=0.05)
add_service_to_map("ONE South Pacific Service Loop C", one_south_pacific_service_loop_c, "ONE", offset=True, offset_distance=0.05)

add_service_to_map("Carpenters Kyowa", carpenters_kyowa, "Kyowa Shipping", offset=True, offset_distance=0.055)
add_service_to_map("Carpenters ONE", carpenters_one, "ONE", offset=True, offset_distance=0.055)
add_service_to_map("MSC Noumea Express", msc_noumea_express, "MSC", offset=True, offset_distance=0.06)
add_service_to_map("MSC Oceania Loop 1", msc_oceania_loop_1, "MSC", offset=True, offset_distance=0.06)

add_straight_line_service_to_map("MSC Oceania Loop 1 US Branch", msc_oceania_loop_1_usbranch, "MSC", offset=True, offset_distance=0.06)

add_service_to_map("MSC Oceania Loop 2", msc_oceania_loop_2, "MSC", offset=True, offset_distance=0.06)

add_straight_line_service_to_map("MSC Oceania Loop 2 US Branch", msc_oceania_loop_2_usbranch, "MSC", offset=True, offset_distance=0.06)

add_service_to_map("PFL NZ East Pacific", pfl_nz_east_pacific, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL NZ Westnorth Pacific", pfl_nz_westnorth_pacific, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL AUS Eastwest Pacific", pfl_aus_eastwest_pacific, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL AUS Tahiti", pfl_aus_tahiti, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL LCL Schedule 1", pfl_lcl_schedule_1, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL LCL Schedule 2", pfl_lcl_schedule_2, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL Islands Schedule", pfl_islands_schedule, "PFL", offset=True, offset_distance=0.065)
add_service_to_map("PFL Fiji Schedule", pfl_fiji_schedule, "PFL", offset=True, offset_distance=0.065)

#-------------------------------------------------------------------------------------------------------------------------------
#mapping finalisation

#add layer control for map
folium.LayerControl().add_to(pacific_map)

#REINSERT BRANCHES HERE IF YOU WANT!!!!!

#add legend
legend_html = """
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 260px; height: auto; 
    background-color: white; z-index:1000; 
    padding: 10px; border: 2px solid grey; border-radius: 5px; font-size: 14px;">
    <b>Legend</b><br>
    <span style="font-size:12px; font-style:italic;">Shipping Operators</span><br>
    <i style="background:red; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Swire Shipping<br>
    <i style="background:blue; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> ANL<br>
    <i style="background:green; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> NPDL<br>
    <i style="background:pink; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> MELL<br>
    <i style="background:orange; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Matson<br>
    <i style="background:purple; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> MAERSK<br>
    <i style="background:yellow; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Kyowa Shipping<br>
    <i style="background:grey; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> CMA CGM<br>
    <i style="background:darkblue; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> NYK<br>
    <i style="background:lightgrey; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> ONE<br>
    <i style="background:black; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> PFL<br>
    <i style="background:darkgreen; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> MSC<br>
    <i style="background:lightblue; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Carpenters Shipping<br>
    <i style="background:cyan; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Nauru Shipping Line<br>
    <span style="font-size:12px; font-style:italic;">Government Charters</span><br>
    <i style="background:cadetblue; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Government of Tokelau<br>
    <i style="background:beige; width:10px; height:10px; display:inline-block; margin-right: 5px;"></i> Government of the Pitcairn Islands<br>
    </div>
</div>
"""
pacific_map.get_root().html.add_child(Element(legend_html))


#save map
pacific_map.save("pacificshippinmap.html")
print("Map saved as 'pacificshippingmap.html'")


#DATA COUNTING

from collections import defaultdict

def analyse_connectivity_metrics(routes, country_ports, route_operators):
    """
    analyse connectivity metrics for PICTs based on routes and operators.

    Args:
    - routes (dict): Dictionary of route names and their port lists.
    - country_ports (dict): Dictionary mapping countries to their ports.
    - route_operators (dict): Dictionary mapping route names to service providers/operators.

    Returns:
    - connectivity_metrics (dict): Calculated connectivity metrics for each country.
    """
    #initialise metrics dictionary
    connectivity_metrics = defaultdict(lambda: {
        "port_frequency": 0,          #how often ports in the country appear in routes
        "connections": set(),         #unique countries connected to this country
        "routes_count": set(),        #unique routes passing through this country
        "service_providers": set(),   #unique operators serving this country
    })

    #iterate through all routes
    for route_name, route_ports in routes.items():
        operator = route_operators.get(route_name, "Unknown")  #get operator for the route
        visited_countries = set()

        for i, port in enumerate(route_ports):
            #identify the country for the current port
            for country, ports in country_ports.items():
                if port in ports:
                    #update Port Frequency
                    connectivity_metrics[country]["port_frequency"] += 1
                    
                    #update Routes Count (add route to set to avoid duplicates)
                    connectivity_metrics[country]["routes_count"].add(route_name)
                    
                    #update Service Providers (add operator to set)
                    connectivity_metrics[country]["service_providers"].add(operator)

                    #track connected countries
                    if i > 0:  #previous port
                        prev_port = route_ports[i - 1]
                        for conn_country, conn_ports in country_ports.items():
                            if prev_port in conn_ports and conn_country != country:
                                connectivity_metrics[country]["connections"].add(conn_country)
                    if i < len(route_ports) - 1:  #next port
                        next_port = route_ports[i + 1]
                        for conn_country, conn_ports in country_ports.items():
                            if next_port in conn_ports and conn_country != country:
                                connectivity_metrics[country]["connections"].add(conn_country)
                    
                    visited_countries.add(country)
                    break

    #finalise metrics by converting sets to counts
    for country, metrics in connectivity_metrics.items():
        metrics["connections"] = len(metrics["connections"])  #count of unique connections
        metrics["routes_count"] = len(metrics["routes_count"])  #count of unique routes
        metrics["service_providers"] = len(metrics["service_providers"])  #count of unique operators

    return connectivity_metrics


country_ports = {
    "American Samoa": ["Pago Pago, American Samoa"],
    "Cook Islands": ["Rarotonga, Cook Islands", "Aitutaki, Cook Islands"],
    "Fiji": ["Suva, Fiji", "Lautoka, Fiji"],
    "French Polynesia": ["Papeete, French Polynesia"],
    "Guam": ["Guam"],
    "Kiribati": ["Tarawa, Kiribati", "Kiritimati, Kiribati"],
    "Marshall Islands": ["Majuro, Marshall Islands", "Ebeye, Marshall Islands", "Kwajalein, Marshall Islands"],
    "Micronesia": ["Chuuk, Micronesia", "Pohnpei, Micronesia", "Kosrae, Micronesia", "Yap, Micronesia"],
    "Nauru": ["Nauru"],
    "New Caledonia": ["Noumea, New Caledonia", "Prony Bay, New Caledonia"],
    "Niue": ["Niue"],
    "Northern Mariana Islands": ["Saipan, Northern Mariana Islands", "Tinian, Northern Mariana Islands"],
    "Palau": ["Koror, Palau"],
    "Papua New Guinea": ["Lae, Papua New Guinea", "Motukea, Papua New Guinea", "Rabaul, Papua New Guinea", 
                         "Madang, Papua New Guinea", "Kimbe, Papua New Guinea", "Wewak, Papua New Guinea"],
    "Pitcairn Islands": ["Pitcairn Island"],
    "Samoa": ["Apia, Samoa"],
    "Solomon Islands": ["Honiara, Solomon Islands", "Noro, Solomon Islands"],
    "Tokelau": ["Atafu, Tokelau", "Fakaofo, Tokelau", "Nukunonu, Tokelau"],
    "Tonga": ["Nuku'alofa, Tonga", "Vava'u, Tonga"],
    "Tuvalu": ["Funafuti, Tuvalu"],
    "Vanuatu": ["Port Vila, Vanuatu", "Santo, Vanuatu"],
    "Wallis & Futuna": ["Wallis, Wallis and Futuna", "Futuna, Wallis and Futuna"],
}


all_routes = {
    #main Routes
    "North Asia Service": north_asia_service,
    "Pacific Islands Service": pacific_islands_service,
    "North Asia Express": north_asia_express,
    "Pacific Weekly Express": pacific_weekly_express,
    "PNG Service": png_service,
    "US West Coast - Pacific Islands Service": us_west_coast_pacific_islands_service,
    "Micronesia Service": micronesia_service,
    "Pacific North Asia Service - Loop 1": pacific_north_asia_service_loop_1,
    "Pacific North Asia Service - Loop 2": pacific_north_asia_service_loop_2,
    "Pacific North Asia Service - Loop 3": pacific_north_asia_service_loop_3,
    "New Zealand Eastern Pacific Service": new_zealand_eastern_pacific_service,

    #ANL Routes
    "APR Service": apr_service,
    "NZ-Fiji Service ANL": nz_fiji_service_anl,
    "PCX Service": pcx_service,
    "Tahiti Service": tahiti_service,
    "WESTPAC Service": westpac_service,
    "AUSPAC Service": auspac_service,
    "SOUTHPAC Service": southpac_service,
    "ANZ Shuttle Service": anz_shuttle_service,
    "ANZ Wallis-Futuna Service": anz_wallis_futuna_service,
    "ANZPAC Service": anzpac_service,

    #NPDL Routes
    "NZ-Fiji Service NPDL": nz_fiji_service_npdl,
    "NZ-Samoa, American Samoa, Tonga Service": nz_samoa_american_samoa_tonga_service,
    "NZ-New Caledonia, Vanuatu Service": nz_new_caledonia_vanuatu_service,
    "NZ-Vanuatu Service": nz_vanuatu_service,
    "NZ-Tahiti Service": nz_tahiti_service,
    "NZ-Tuvalu, Wallis and Futuna, Kiribati Service": nz_tuvalu_wallis_futuna_kiribati_service,
    "NZ-Marshall Islands, Micronesia, Solomon Islands Service": nz_marshall_islands_micronesia_solomon_islands_service,
    "NZ-Cook Islands Service": nz_cook_islands_service,
    "NZ-Honiara Service": nz_honiara_service,
    "AUS-Fiji, Samoa, Tonga Service": aus_fiji_samoa_tonga_service,
    "AUS-Tahiti, Tonga Service": aus_tahiti_tonga_service,
    "AUS-New Caledonia Service": aus_new_caledonia_service,
    "AUS-Vanuatu Service": aus_vanuatu_service,
    "AUS-Tuvalu, Wallis and Futuna, Kiribati Service": aus_tuvalu_wallis_futuna_kiribati_service,
    "AUS-Solomon Islands Service": aus_solomon_islands_service,
    "AUS-Cook Islands Service": aus_cook_islands_service,
    "FJ-Samoa, American Samoa, Tonga, NZ Service": fj_samoa_american_samoa_tonga_nz_service,
    "FJ-AUS Service": fj_aus_service,
    "FJ-Vanuatu Service": fj_vanuatu_service,
    "FJ-Tuvalu, Wallis and Futuna, Kiribati Service": fj_tuvalu_wallis_futuna_kiribati_service,
    "FJ-Marshall Islands, Micronesia, Solomon Islands Service": fj_marshall_islands_micronesia_solomon_islands_service,
    "Samoa, American Samoa, Tonga-NZ, AUS Service": samoa_american_samoa_tonga_nz_aus_service,
    "New Caledonia-NZ Service": new_caledonia_nz_service,
    "Vanuatu-NZ Service": vanuatu_nz_service,
    "New Caledonia, Vanuatu-NZ Service": new_caledonia_vanuatu_nz_service,
    "New Caledonia-Wallis and Futuna, Vanuatu Service": new_caledonia_wallis_futuna_vanuatu_service,
    "New Caledonia-Fiji, Wallis and Futuna Service": new_caledonia_fiji_wallis_futuna_service,

    #CALPAC Routes
    "CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service": calpac_us_tahiti_samoa_american_samoa_tonga_service,
    "CALPAC US-NZ, AUS Service": calpac_us_nz_aus_service,
    "CALPAC US-New Caledonia, Vanuatu Service": calpac_us_new_caledonia_vanuatu_service,
    "CALPAC Tuvalu, Wallis and Futuna, Kiribati Service": calpac_tuvalu_wallis_futuna_kiribati_service,
    "CALPAC AUS, NZ, Fiji, Tahiti-US Service": calpac_aus_nz_fiji_tahiti_us_service,
    "South Pacific Service": south_pacific_service,

    #MELL Routes
    "NZ-Guam, Saipan, Micronesia": nz_guam_saipan_micronesia,

    #Matson Routes
    "Matson South Pacific Shipping Service": matson_south_pacific_shipping,
    "Matson Guam and Micronesia Shipping Service": matson_guam_and_micronesia_shipping_service,

    #MAERSK Routes
    "Fiji Express Service": fiji_express_service,
    "PNG Express Service": png_express_service,

    #PIL Routes converted to MELL
    "ANA Service": ana_service,
    "MXS Service": mxs_service,
    "EMS Service": ems_service,
    "MSP Service": msp_service,

    #Kyowa Shipping Routes
    "Saipan, Guam, Micronesia Service": saipan_guam_micronesia_service,
    "South Pacific Islands Service": south_pacific_islands_service,
    "PNG-AUS Service": png_aus_service,

    #Nauru Shipping Line Routes
    "NSL Micronesian Pride Service": nsl_micronesian_pride_service,
    "NSL Supplementary Service": nsl_supplementary_service,

    #Government of Tokelau Routes
    "Department of Transport & Support Services Service": department_transport_tokelau,

    #Government of the Pitcairn Islands Routes
    "MV Silver Supporter Regular Service": mv_silver_supporter_regular,
    "MV Silver Supporter NZ Freight Run Service": mv_silver_supporter_nz_freight_run_service,

    #extra branches
    "US West Coast - Pacific Extra Branch 1": us_west_coast_pacific_extra_branch_1,
    "US West Coast - Pacific Extra Branch 2": us_west_coast_pacific_extra_branch_2,
    "US West Coast - Pacific Extra Branch 3": us_west_coast_pacific_extra_branch_3,
    "PCX US Branch 1": pcx_us_branch_1,
    "PCX US Branch 2": pcx_us_branch_2,
    "PCX US Branch 3": pcx_us_branch_3,
    "PCX Pacific Branch 1": pcx_pacific_branch_1,
    "PCX Pacific Branch 2": pcx_pacific_branch_2,
    "Matson Guam Micronesia US Branch 1": matson_guam_micronesia_us_branch_1,
    "Matson Guam Micronesia Pacific Branch 1": matson_guam_micronesia_pacific_branch_1,
    "Matson Guam Micronesia US Branch 2": matson_guam_micronesia_us_branch_2,
    "Matson Guam Micronesia Pacific Branch 2": matson_guam_micronesia_pacific_branch_2,
    "PNG Service Extra Branch 1": png_service_extra_branch_1,
    "PNG Service Extra Branch 2": png_service_extra_branch_2,
    "PNG Service Extra Branch 3": png_service_extra_branch_3,
    "PNG Service Extra Branch 4": png_service_extra_branch_4,
    "NZ Eastern Pacific Extra Branch 1": nz_eastern_pacific_extra_branch_1,
    "NZ Eastern Pacific Extra Branch 2": nz_eastern_pacific_extra_branch_2,
    "NZ Eastern Pacific Extra Branch 3": nz_eastern_pacific_extra_branch_3,
    "Swire Pacific Extra Branch 1": swire_pacific_extra_branch_1,
    "Swire Pacific Extra Branch 2": swire_pacific_extra_branch_2,

    #NEW
    "NYK South Pacific Link": nyk_south_pacific_link,
    "CMA PAD Service": cma_pad_service,
    "CMA PAD Service US Branch": cma_pad_service_usbranch,
    "ONE South Pacific Service Loop A": one_south_pacific_service_loop_a,
    "ONE South Pacific Service Loop B": one_south_pacific_service_loop_b,
    "ONE South Pacific Service Loop C": one_south_pacific_service_loop_c,
    "Carpenters Kyowa": carpenters_kyowa,
    "Carpenters ONE": carpenters_one,
    "MSC Noumea Express": msc_noumea_express,
    "MSC Oceania Loop 1": msc_oceania_loop_1,
    "MSC Oceania Loop 1 US Branch": msc_oceania_loop_1_usbranch,
    "MSC Oceania Loop 2": msc_oceania_loop_2,
    "MSC Oceania Loop 2 US Branch": msc_oceania_loop_2_usbranch,
    "PFL NZ East Pacific": pfl_nz_east_pacific,
    "PFL NZ WestNorth Pacific": pfl_nz_westnorth_pacific,
    "PFL AUS EastWest Pacific": pfl_aus_eastwest_pacific,
    "PFL AUS Tahiti": pfl_aus_tahiti,
    "PFL LCL Schedule 1": pfl_lcl_schedule_1,
    "PFL LCL Schedule 2": pfl_lcl_schedule_2,
    "PFL Islands Schedule": pfl_islands_schedule,
    "PFL Fiji Schedule": pfl_fiji_schedule,
}

route_operators = {
    #Swire Shipping
    "North Asia Service": "Swire Shipping",
    "Pacific Islands Service": "Swire Shipping",
    "North Asia Express": "Swire Shipping",
    "Pacific Weekly Express": "Swire Shipping",
    "PNG Service": "Swire Shipping",
    "US West Coast - Pacific Islands Service": "Swire Shipping",
    "Micronesia Service": "Swire Shipping",
    "Pacific North Asia Service - Loop 1": "Swire Shipping",
    "Pacific North Asia Service - Loop 2": "Swire Shipping",
    "Pacific North Asia Service - Loop 3": "Swire Shipping",
    "New Zealand Eastern Pacific Service": "Swire Shipping",

    #ANL Routes
    "APR Service": "ANL",
    "NZ-Fiji Service ANL": "ANL",
    "PCX Service": "ANL",
    "Tahiti Service": "ANL",
    "WESTPAC Service": "ANL",
    "AUSPAC Service": "ANL",
    "SOUTHPAC Service": "ANL",
    "ANZ Shuttle Service": "ANL",
    "ANZ Wallis-Futuna Service": "ANL",
    "ANZPAC Service": "ANL",

    #NPDL Routes
    "NZ-Fiji Service NPDL": "NPDL",
    "NZ-Samoa, American Samoa, Tonga Service": "NPDL",
    "NZ-New Caledonia, Vanuatu Service": "NPDL",
    "NZ-Vanuatu Service": "NPDL",
    "NZ-Tahiti Service": "NPDL",
    "NZ-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "NZ-Marshall Islands, Micronesia, Solomon Islands Service": "NPDL",
    "NZ-Cook Islands Service": "NPDL",
    "NZ-Honiara Service": "NPDL",
    "AUS-Fiji, Samoa, Tonga Service": "NPDL",
    "AUS-Tahiti, Tonga Service": "NPDL",
    "AUS-New Caledonia Service": "NPDL",
    "AUS-Vanuatu Service": "NPDL",
    "AUS-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "AUS-Solomon Islands Service": "NPDL",
    "AUS-Cook Islands Service": "NPDL",
    "FJ-Samoa, American Samoa, Tonga, NZ Service": "NPDL",
    "FJ-AUS Service": "NPDL",
    "FJ-Vanuatu Service": "NPDL",
    "FJ-Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "FJ-Marshall Islands, Micronesia, Solomon Islands Service": "NPDL",
    "Samoa, American Samoa, Tonga-NZ, AUS Service": "NPDL",
    "New Caledonia-NZ Service": "NPDL",
    "Vanuatu-NZ Service": "NPDL",
    "New Caledonia, Vanuatu-NZ Service": "NPDL",
    "New Caledonia-Wallis and Futuna, Vanuatu Service": "NPDL",
    "New Caledonia-Fiji, Wallis and Futuna Service": "NPDL",
    "CALPAC US-Tahiti, Samoa, American Samoa, Tonga Service": "NPDL",
    "CALPAC US-NZ, AUS Service": "NPDL",
    "CALPAC US-New Caledonia, Vanuatu Service": "NPDL",
    "CALPAC Tuvalu, Wallis and Futuna, Kiribati Service": "NPDL",
    "CALPAC AUS, NZ, Fiji, Tahiti-US Service": "NPDL",
    "South Pacific Service": "NPDL",

    #MELL Routes
    "NZ-Guam, Saipan, Micronesia": "MELL",
    "ANA Service": "MELL",
    "MXS Service": "MELL",
    "EMS Service": "MELL",
    "MSP Service": "MELL",

    #Matson Routes
    "Matson South Pacific Shipping Service": "Matson",
    "Matson Guam and Micronesia Shipping Service": "Matson",

    #MAERSK Routes
    "Fiji Express Service": "MAERSK",
    "PNG Express Service": "MAERSK",

    #Kyowa Shipping Routes
    "Saipan, Guam, Micronesia Service": "Kyowa",
    "South Pacific Islands Service": "Kyowa",
    "PNG-AUS Service": "Kyowa",

    #Nauru Shipping Line Routes
    "NSL Micronesian Pride Service": "NSL",
    "NSL Supplementary Service": "NSL",

    #Government of Tokelau Routes
    "Department of Transport & Support Services Service": "Government of Tokelau",

    #Government of the Pitcairn Islands Routes
    "MV Silver Supporter Regular Service": "Government of the Pitcairn Islands",
    "MV Silver Supporter NZ Freight Run Service": "Government of the Pitcairn Islands",

    #extra branches
    "US West Coast - Pacific Extra Branch 1": "Extra",
    "US West Coast - Pacific Extra Branch 2": "Extra",
    "US West Coast - Pacific Extra Branch 3": "Extra",
    "PCX US Branch 1": "Extra",
    "PCX US Branch 2": "Extra",
    "PCX US Branch 3": "Extra",
    "PCX Pacific Branch 1": "Extra",
    "PCX Pacific Branch 2": "Extra",
    "Matson Guam Micronesia US Branch 1": "Matson",
    "Matson Guam Micronesia Pacific Branch 1": "Matson",
    "Matson Guam Micronesia US Branch 2": "Matson",
    "Matson Guam Micronesia Pacific Branch 2": "Matson",
    "PNG Service Extra Branch 1": "Extra",
    "PNG Service Extra Branch 2": "Extra",
    "PNG Service Extra Branch 3": "Extra",
    "PNG Service Extra Branch 4": "Extra",
    "NZ Eastern Pacific Extra Branch 1": "Extra",
    "NZ Eastern Pacific Extra Branch 2": "Extra",
    "NZ Eastern Pacific Extra Branch 3": "Extra",
    "Swire Pacific Extra Branch 1": "Extra",
    "Swire Pacific Extra Branch 2": "Extra",

    #NEW
    "NYK South Pacific Link": "NYK",
    "CMA PAD Service": "CMA CGM",
    "CMA PAD Service US Branch": "CMA CGM",
    "ONE South Pacific Service Loop A": "ONE",
    "ONE South Pacific Service Loop B": "ONE",
    "ONE South Pacific Service Loop C": "ONE",
    "Carpenters Kyowa": "Kyowa",
    "Carpenters ONE": "ONE",
    "MSC Noumea Express": "MSC",
    "MSC Oceania Loop 1": "MSC",
    "MSC Oceania Loop 1 US Branch": "MSC",
    "MSC Oceania Loop 2": "MSC",
    "MSC Oceania Loop 2 US Branch": "MSC",
    "PFL NZ East Pacific": "PFL",
    "PFL NZ WestNorth Pacific": "PFL",
    "PFL AUS EastWest Pacific": "PFL",
    "PFL AUS Tahiti": "PFL",
    "PFL LCL Schedule 1": "PFL",
    "PFL LCL Schedule 2": "PFL",
    "PFL Islands Schedule": "PFL",
    "PFL Fiji Schedule": "PFL",
}



connectivity_metrics = analyse_connectivity_metrics(all_routes, country_ports, route_operators)
import pandas as pd

metrics_df = pd.DataFrame.from_dict(connectivity_metrics, orient="index").reset_index()
metrics_df.columns = ["Country", "Port Frequency", "Connections", "Routes Count", "Service Providers"]

metrics_df.to_csv("connectivity_metrics.csv", index=False)
print("Connectivity metrics have been saved to 'connectivity_metrics.csv'.")
#print(metrics_df)

#extra density map for routes

def create_density_map_from_variables(city_coords):
    """
    Create a density map with straight lines for route legs based on individual route variables.
    Saves the map as 'DENSITY.html'.

    Args:
    - city_coords (dict): Dictionary with city coordinates {city_name: (latitude, longitude)}.

    Returns:
    - None.
    """
    import os

    #dynamically collect all route variables
    route_variables = [
    north_asia_service,
    pacific_islands_service,
    north_asia_express,
    pacific_weekly_express,
    png_service,
    us_west_coast_pacific_islands_service,
    micronesia_service,
    pacific_north_asia_service_loop_1,
    pacific_north_asia_service_loop_2,
    pacific_north_asia_service_loop_3,
    new_zealand_eastern_pacific_service,
    apr_service,
    nz_fiji_service_anl,
    pcx_service,
    tahiti_service,
    westpac_service,
    auspac_service,
    southpac_service,
    anz_shuttle_service,
    anz_wallis_futuna_service,
    anzpac_service,
    nz_fiji_service_npdl,
    nz_samoa_american_samoa_tonga_service,
    nz_new_caledonia_vanuatu_service,
    nz_vanuatu_service,
    nz_tahiti_service,
    nz_tuvalu_wallis_futuna_kiribati_service,
    nz_marshall_islands_micronesia_solomon_islands_service,
    nz_cook_islands_service,
    nz_honiara_service,
    aus_fiji_samoa_tonga_service,
    aus_tahiti_tonga_service,
    aus_new_caledonia_service,
    aus_vanuatu_service,
    aus_tuvalu_wallis_futuna_kiribati_service,
    aus_solomon_islands_service,
    aus_cook_islands_service,
    fj_samoa_american_samoa_tonga_nz_service,
    fj_aus_service,
    fj_vanuatu_service,
    fj_tuvalu_wallis_futuna_kiribati_service,
    fj_marshall_islands_micronesia_solomon_islands_service,
    samoa_american_samoa_tonga_nz_aus_service,
    new_caledonia_nz_service,
    vanuatu_nz_service,
    new_caledonia_vanuatu_nz_service,
    new_caledonia_wallis_futuna_vanuatu_service,
    new_caledonia_fiji_wallis_futuna_service,
    calpac_us_tahiti_samoa_american_samoa_tonga_service,
    calpac_us_nz_aus_service,
    calpac_us_new_caledonia_vanuatu_service,
    calpac_tuvalu_wallis_futuna_kiribati_service,
    calpac_aus_nz_fiji_tahiti_us_service,
    south_pacific_service,
    nz_guam_saipan_micronesia,
    matson_south_pacific_shipping,
    matson_guam_and_micronesia_shipping_service,
    fiji_express_service,
    png_express_service,
    ana_service,
    mxs_service,
    ems_service,
    msp_service,
    saipan_guam_micronesia_service,
    south_pacific_islands_service,
    png_aus_service,
    nsl_micronesian_pride_service,
    nsl_supplementary_service,
    department_transport_tokelau,
    mv_silver_supporter_regular,
    mv_silver_supporter_nz_freight_run_service,
    us_west_coast_pacific_islands_us_branch_1,
    us_west_coast_pacific_islands_us_branch_2,
    us_west_coast_pacific_islands_pacific_branch,
    us_west_coast_pacific_extra_branch_1,
    us_west_coast_pacific_extra_branch_2,
    us_west_coast_pacific_extra_branch_3,
    pcx_us_branch_1,
    pcx_us_branch_2,
    pcx_us_branch_3,
    pcx_pacific_branch_1,
    pcx_pacific_branch_2,
    matson_guam_micronesia_us_branch_1,
    matson_guam_micronesia_pacific_branch_1,
    matson_guam_micronesia_us_branch_2,
    matson_guam_micronesia_pacific_branch_2,
    png_service_extra_branch_1,
    png_service_extra_branch_2,
    png_service_extra_branch_3,
    png_service_extra_branch_4,
    nz_eastern_pacific_extra_branch_1,
    nz_eastern_pacific_extra_branch_2,
    nz_eastern_pacific_extra_branch_3,
    swire_pacific_extra_branch_1,
    swire_pacific_extra_branch_2,
    nyk_south_pacific_link,
    cma_pad_service,
    cma_pad_service_usbranch,
    one_south_pacific_service_loop_a,
    one_south_pacific_service_loop_b,
    one_south_pacific_service_loop_c,
    carpenters_kyowa,
    carpenters_one,
    msc_noumea_express,
    msc_oceania_loop_1,
    msc_oceania_loop_1_usbranch,
    msc_oceania_loop_2,
    msc_oceania_loop_2_usbranch,
    pfl_nz_east_pacific,
    pfl_nz_westnorth_pacific,
    pfl_aus_eastwest_pacific,
    pfl_aus_tahiti,
    pfl_lcl_schedule_1,
    pfl_lcl_schedule_2,
    pfl_islands_schedule,
    pfl_fiji_schedule,
]

    #initialise map
    density_map = folium.Map(location=[-15, 160], zoom_start=3, tiles="OpenStreetMap") #cartodbpositron was grey background

    #dictionary to track leg frequencies
    route_legs = defaultdict(int)

    #count frequencies of all route legs
    for route_ports in route_variables:
        for i in range(len(route_ports) - 1):
            start_port = route_ports[i]
            end_port = route_ports[i + 1]
            leg = tuple(sorted([start_port, end_port]))  # Order-independent leg
            route_legs[leg] += 1

    #add lines to the map
    for leg, frequency in route_legs.items():
        start_port, end_port = leg
        start_coords = city_coords.get(start_port)
        end_coords = city_coords.get(end_port)

        if not start_coords or not end_coords:
            print(f"Skipping leg: {start_port} ↔ {end_port} due to missing coordinates.")
            continue

        #define the route as a straight line
        route = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [start_coords[1], start_coords[0]],  # Longitude, Latitude
                    [end_coords[1], end_coords[0]],
                ],
            },
        }

        #add line to the map with thickness based on frequency
        folium.GeoJson(
            route,
            style_function=lambda x, freq=frequency: {
                "color": "blue",
                "weight": 1 + freq * 0.5,  # Line thickness based on frequency
                "opacity": 0.7,
            },
        ).add_to(density_map)

    #save the map
    density_map.save("DENSITY.html")
    print("Density map saved as 'DENSITY.html'.")

create_density_map_from_variables(city_coords)