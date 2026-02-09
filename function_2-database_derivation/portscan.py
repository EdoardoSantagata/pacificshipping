import requests
from datetime import datetime, timedelta
import os
import pandas as pd
import time
import zipfile
import glob
import json
import csv
import shutil

API_KEY = #insert API key
BASE_REPORT_URL = "https://api.datalastic.com/api/v0/report"

# Adjusted function to handle a maximum of 7 days per request
def split_date_range_7_days(start_date, end_date):
    date_ranges = []
    current_start = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=7), end_date)
        date_ranges.append((current_start.date().isoformat(), current_end.date().isoformat()))
        current_start = current_end + timedelta(days=1)
    return date_ranges

def submit_report_request(lat_port, lon_port, radius, start_date, end_date):
    date_ranges = split_date_range_7_days(start_date, end_date)  # Split into 7-day chunks
    report_ids = []

    for start, end in date_ranges:
        payload = {
            "api-key": API_KEY,
            "report_type": "inradius_history",
            "lat": lat_port,
            "lon": lon_port,
            "radius": radius,
            "from": start,
            "to": end
        }
        print(f"Submitting report request for {start} to {end}...")
        try:
            response = requests.post(BASE_REPORT_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            report_id = data.get("data", {}).get("report_id")
            if report_id:
                print(f"Report submitted successfully. Report ID: {report_id}")
                report_ids.append(report_id)
            else:
                print(f"Failed to retrieve report ID for range {start} to {end}.")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting report request for range {start} to {end}: {e}")
    return report_ids

def check_report_status(report_id, max_retries=60, wait_time=30):
    """
    Poll the report status until it's ready, failed, or times out.
    Retries several times with wait time in between.

    :param report_id: The report ID to check the status of.
    :param max_retries: Maximum number of retries.
    :param wait_time: Time to wait (in seconds) between each retry.
    :return: The download URL if the report is ready, None if failed or not ready after retries.
    """
    try:
        retries = 0
        while retries < max_retries:
            status_url = f"https://api.datalastic.com/api/v0/report?api-key={API_KEY}&report_id={report_id}"
            print(f"DEBUG: Checking status for report ID -> {report_id}, Retry #{retries + 1}")
            response = requests.get(status_url)
            
            if response.status_code == 404:
                print(f"DEBUG: Report ID {report_id} not found. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)
                continue  # Retry if report isn't found
            
            response.raise_for_status()  # Raise an error if the status code is not 200

            data = response.json()
            print(f"DEBUG: Report status response -> {data}")

            status = data.get("data", {}).get("status")
            if status == "_DONE_":  # Report is done
                print(f"Report ID {report_id} is ready.")
                return data.get("data", {}).get("result_url")
            elif status == "failed":  # Report generation failed
                print(f"Report ID {report_id} generation failed.")
                return None
            else:
                print(f"Report ID {report_id} status: {status}. Retrying in {wait_time} seconds...")
                retries += 1
                time.sleep(wait_time)
                
        print(f"Timed out waiting for report ID {report_id}.")
        return None  # If all retries are exhausted, return None

    except requests.exceptions.RequestException as e:
        print(f"Error checking status for report ID {report_id}: {e}")
        return None

def copy_csv_to_raw_reports(csv_file):
    """
    Copies the CSV file to the 'raw_reports' folder.
    """
    if not os.path.exists("raw_reports"):
        os.makedirs("raw_reports")  # Create the directory if it doesn't exist
    
    raw_csv_path = os.path.join("raw_reports", os.path.basename(csv_file))
    shutil.copy(csv_file, raw_csv_path)
    print(f"CSV file copied to raw_reports: {raw_csv_path}")

def download_report_data(download_url):
    try:
        response = requests.get(download_url)
        response.raise_for_status()
        zip_file_path = "temp_report.zip"
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)
        print(f"Report downloaded and saved to {zip_file_path}")

        # Extract ZIP content
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall("temp_extracted")
        print("Report extracted.")

        # Check the files in the extracted directory
        extracted_files = os.listdir("temp_extracted")
        print(f"Extracted files: {extracted_files}")

        # Look for the .csv file and process it
        csv_files = glob.glob("temp_extracted/*.csv")
        if not csv_files:
            print("No CSV files found in the extracted report.")
            return []

        # Process the CSV file
        csv_file = csv_files[0]
        print(f"Processing CSV file: {csv_file}")

        # Copy the CSV file to 'raw_reports' folder
        copy_csv_to_raw_reports(csv_file)

        # Process the CSV file
        vessels = []
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Extract the UUID and add the corresponding report ID
                vessels.append({
                    "uuid": row.get("uuid"),
                    "report_id": row.get("report_id")  # report_id from the report, will need to be passed along
                })
        
        # Remove duplicates by UUID
        unique_vessels = {vessel["uuid"]: vessel for vessel in vessels}.values()

        print(f"Extracted {len(unique_vessels)} unique vessels.")
        return unique_vessels
    except Exception as e:
        print(f"Error downloading or processing report: {e}")
        return []
    finally:
        if os.path.exists("temp_report.zip"):
            os.remove("temp_report.zip")
        if os.path.exists("temp_extracted"):
            import shutil
            shutil.rmtree("temp_extracted", ignore_errors=True)

def save_to_excel(data, lat_port, lon_port, start_date, end_date):
    # Dictionary mapping lat/lon to country and port names
    port_info = {
        (-14.17503, -169.6433): {"country": "American Samoa", "port_name": "Ofu"},
        (-14.27778, -170.6813): {"country": "American Samoa", "port_name": "Pago Pago"},
        (-14.22845, -169.5064): {"country": "American Samoa", "port_name": "Tau"},
        (-18.86949, -159.7882): {"country": "Cook Islands", "port_name": "Aitutaki"},
        (-20.00706, -158.1128): {"country": "Cook Islands", "port_name": "Atiu"},
        (-21.92011, -157.9155): {"country": "Cook Islands", "port_name": "Mangaia"},
        (-20.16006, -157.34): {"country": "Cook Islands", "port_name": "Mauke Island"},
        (-19.87151, -157.7051): {"country": "Cook Islands", "port_name": "Mitiaro Island"},
        (-21.20418, -159.7844): {"country": "Cook Islands", "port_name": "Rarotonga"},
        (-17.7325, -179.3218): {"country": "Fiji", "port_name": "Cicia"},
        (-16.36317, 179.3642): {"country": "Fiji", "port_name": "Labasa"},
        (-17.614, 177.4456): {"country": "Fiji", "port_name": "Lautoka"},
        (-17.68332, 178.8267): {"country": "Fiji", "port_name": "Levuka"},
        (-17.6767, 177.106): {"country": "Fiji", "port_name": "Mana Island"},
        (-17.77272, 177.1933): {"country": "Fiji", "port_name": "Maolo Lailai Island"},
        (-18.56165, 179.9389): {"country": "Fiji", "port_name": "Moala"},
        (-16.99391, 178.687): {"country": "Fiji", "port_name": "Nabouwalu"},
        (-17.77485, 177.389): {"country": "Fiji", "port_name": "Nadi"},
        (-17.67993, 178.584): {"country": "Fiji", "port_name": "Natovi"},
        (-16.52851, 179.9765): {"country": "Fiji", "port_name": "Rabi"},
        (-16.77734, 179.333): {"country": "Fiji", "port_name": "Savusavu"},
        (-18.14128, 177.5086): {"country": "Fiji", "port_name": "Singatoka"},
        (-18.12138, 178.4164): {"country": "Fiji", "port_name": "Suva"},
        (-16.79776, 179.9937): {"country": "Fiji", "port_name": "Tavuki"},
        (-16.95887, 177.373): {"country": "Fiji", "port_name": "Turtle Island"},
        (-17.21324, -178.932): {"country": "Fiji", "port_name": "Vanua Mbalavu"},
        (-18.51245, 177.6365): {"country": "Fiji", "port_name": "Vatulele"},
        (-17.68737, 177.3851): {"country": "Fiji", "port_name": "Vuda"},
        (-16.94145, 178.6602): {"country": "Fiji", "port_name": "Wairiki"},
        (-16.70838, 177.5791): {"country": "Fiji", "port_name": "Yasawa Island"},
        (-9.805827, -139.0367): {"country": "French Polynesia", "port_name": "Atuona"},
        (-16.5041, -151.7383): {"country": "French Polynesia", "port_name": "Bora Bora"},
        (-10.49422, -138.6609): {"country": "French Polynesia", "port_name": "Fatu Hiva"},
        (-9.739342, -138.9455): {"country": "French Polynesia", "port_name": "Hiva Oa"},
        (-16.44662, -152.2619): {"country": "French Polynesia", "port_name": "Maupiti"},
        (-17.5285, -149.572): {"country": "French Polynesia", "port_name": "Papeete"},
        (-16.05644, -145.6208): {"country": "French Polynesia", "port_name": "Rotoava"},
        (-8.907501, -140.1004): {"country": "French Polynesia", "port_name": "Taiohae"},
        (-16.99359, -149.575): {"country": "French Polynesia", "port_name": "Tetiaroa"},
        (-8.927046, -139.561): {"country": "French Polynesia", "port_name": "Ua Huka"},
        (-9.411129, -140.11): {"country": "French Polynesia", "port_name": "Ua Pou"},
        (-16.7316, -151.4514): {"country": "French Polynesia", "port_name": "Uturoa"},
        (-17.5225, -149.7775): {"country": "French Polynesia", "port_name": "Vaiare Harbor"},
        (13.44447, 144.6515): {"country": "Guam", "port_name": "Guam"},
        (1.365622, 172.934): {"country": "Kiribati", "port_name": "Betio"},
        (3.857249, -159.3601): {"country": "Kiribati", "port_name": "Tabuaeran"},
        (10.22168, 169.9791): {"country": "Marshall Islands", "port_name": "Ailuk Island"},
        (7.066695, 171.5558): {"country": "Marshall Islands", "port_name": "Arno"},
        (11.34171, 162.3221): {"country": "Marshall Islands", "port_name": "Enewetak Island"},
        (11.52483, 165.5643): {"country": "Marshall Islands", "port_name": "Enyu Airfield"},
        (8.728666, 167.7329): {"country": "Marshall Islands", "port_name": "Kwajalein"},
        (9.825882, 169.3055): {"country": "Marshall Islands", "port_name": "Likiep Island"},
        (7.08684, 171.3647): {"country": "Marshall Islands", "port_name": "Majuro"},
        (8.893085, 170.8457): {"country": "Marshall Islands", "port_name": "Maloelap Island"},
        (10.27616, 170.8656): {"country": "Marshall Islands", "port_name": "Mejit Island"},
        (6.037969, 171.9458): {"country": "Marshall Islands", "port_name": "Mili Island"},
        (7.754793, 168.2471): {"country": "Marshall Islands", "port_name": "Namu"},
        (11.16238, 166.8919): {"country": "Marshall Islands", "port_name": "Rongelap Island"},
        (11.22526, 169.8451): {"country": "Marshall Islands", "port_name": "Utirik Island"},
        (10.16677, 166.0077): {"country": "Marshall Islands", "port_name": "Wotho Island"},
        (9.458714, 170.2334): {"country": "Marshall Islands", "port_name": "Wotje Island"},
        (7.445945, 151.8398): {"country": "Micronesia", "port_name": "Chuuk"},
        (5.34676, 162.9561): {"country": "Micronesia", "port_name": "Kosrae"},
        (6.963745, 158.2109): {"country": "Micronesia", "port_name": "Pohnpei"},
        (9.51516, 138.1253): {"country": "Micronesia", "port_name": "Tomil"},
        (14.13674, 145.1338): {"country": "N Mariana Is", "port_name": "Rota"},
        (15.22498, 145.7384): {"country": "N Mariana Is", "port_name": "Saipan"},
        (14.96237, 145.623): {"country": "N Mariana Is", "port_name": "Tinian"},
        (-0.53632, 166.9409): {"country": "Nauru", "port_name": "Nauru Island"},
        (-22.3522, 166.8929): {"country": "New Caledonia", "port_name": "Baie De Prony"},
        (-22.33038, 166.6958): {"country": "New Caledonia", "port_name": "Baie Ngo"},
        (-20.78765, 167.1331): {"country": "New Caledonia", "port_name": "Easo"},
        (-22.658, 167.436): {"country": "New Caledonia", "port_name": "Ile Des Pins"},
        (-21.39642, 165.83): {"country": "New Caledonia", "port_name": "Kouaoua"},
        (-20.58037, 164.2753): {"country": "New Caledonia", "port_name": "Koumac"},
        (-21.14497, 165.5563): {"country": "New Caledonia", "port_name": "Moneo"},
        (-21.3284, 164.9939): {"country": "New Caledonia", "port_name": "Nepoui"},
        (-22.27534, 166.4347): {"country": "New Caledonia", "port_name": "Noumea"},
        (-21.97993, 166.6831): {"country": "New Caledonia", "port_name": "Ouinne"},
        (-20.54961, 166.5625): {"country": "New Caledonia", "port_name": "Ouvea"},
        (-20.49609, 164.17): {"country": "New Caledonia", "port_name": "Paagumene"},
        (-21.29162, 165.7341): {"country": "New Caledonia", "port_name": "Poro"},
        (-21.54709, 167.8764): {"country": "New Caledonia", "port_name": "Tadine"},
        (-20.304, 164.0493): {"country": "New Caledonia", "port_name": "Tanle"},
        (-21.61323, 166.2456): {"country": "New Caledonia", "port_name": "Thio"},
        (-21.00255, 164.6786): {"country": "New Caledonia", "port_name": "Vavouto"},
        (-19.05222, -169.9239): {"country": "Niue", "port_name": "Alofi"},
        (-18.97581, -169.8904): {"country": "Niue", "port_name": "Niue Island"},
        (6.905637, 134.1293): {"country": "Palau", "port_name": "Angaur"},
        (7.348847, 134.4808): {"country": "Palau", "port_name": "Koror"},
        (7.33445, 134.4545): {"country": "Palau", "port_name": "Melekeok"},
        (-10.31577, 150.4727): {"country": "Papua New Guinea", "port_name": "Alotau"},
        (-5.540424, 146.1389): {"country": "Papua New Guinea", "port_name": "Basamuk"},
        (-5.305724, 150.9974): {"country": "Papua New Guinea", "port_name": "Bialla"},
        (-5.433948, 154.6728): {"country": "Papua New Guinea", "port_name": "Buka"},
        (-9.061934, 143.2102): {"country": "Papua New Guinea", "port_name": "Daru"},
        (-2.584816, 150.787): {"country": "Papua New Guinea", "port_name": "Kavieng"},
        (-7.95813, 145.7666): {"country": "Papua New Guinea", "port_name": "Kerema"},
        (-6.217567, 155.6382): {"country": "Papua New Guinea", "port_name": "Kieta"},
        (-5.547617, 150.15): {"country": "Papua New Guinea", "port_name": "Kimbe"},
        (-6.125663, 141.2973): {"country": "Papua New Guinea", "port_name": "Kiunga"},
        (-8.12568, 144.5732): {"country": "Papua New Guinea", "port_name": "Kumul"},
        (-6.741072, 146.9966): {"country": "Papua New Guinea", "port_name": "Lae"},
        (-9.338321, 146.9919): {"country": "Papua New Guinea", "port_name": "Lese"},
        (-3.114462, 152.6465): {"country": "Papua New Guinea", "port_name": "Lihir Island"},
        (-5.212118, 145.8042): {"country": "Papua New Guinea", "port_name": "Madang"},
        (-7.755599, 147.588): {"country": "Papua New Guinea", "port_name": "Morobe"},
        (-8.898132, 148.4947): {"country": "Papua New Guinea", "port_name": "Oro Bay"},
        (-9.447374, 147.1239): {"country": "Papua New Guinea", "port_name": "Port Moresby"},
        (-4.202467, 152.17): {"country": "Papua New Guinea", "port_name": "Rabaul"},
        (-8.43162, 143.76): {"country": "Papua New Guinea", "port_name": "Umuda"},
        (-2.678658, 141.2859): {"country": "Papua New Guinea", "port_name": "Vanimo"},
        (-3.565464, 143.6436): {"country": "Papua New Guinea", "port_name": "Wewak"},
        (-25.06974, -130.1077): {"country": "Pitcairn Is", "port_name": "Pitcairn"},
        (-13.82862, -171.7627): {"country": "Samoa", "port_name": "Apia"},
        (-9.531517, 160.489): {"country": "Solomon Islands", "port_name": "Aola Bay"},
        (-8.776299, 160.6973): {"country": "Solomon Islands", "port_name": "Auki"},
        (-8.102781, 156.8339): {"country": "Solomon Islands", "port_name": "Gizo"},
        (-9.4305, 159.9575): {"country": "Solomon Islands", "port_name": "Honiara"},
        (-10.41537, 161.7826): {"country": "Solomon Islands", "port_name": "Kirakira"},
        (-7.569364, 156.6021): {"country": "Solomon Islands", "port_name": "Malloco Bay"},
        (-8.227547, 157.2086): {"country": "Solomon Islands", "port_name": "Noro"},
        (-11.64902, 160.2798): {"country": "Solomon Islands", "port_name": "Rannell Island"},
        (-8.121561, 157.1119): {"country": "Solomon Islands", "port_name": "Ringgi Cove"},
        (-9.103411, 160.1504): {"country": "Solomon Islands", "port_name": "Tulagi"},
        (-8.492449, 157.722): {"country": "Solomon Islands", "port_name": "Viru Harbour"},
        (-9.078345, 159.2218): {"country": "Solomon Islands", "port_name": "Yandina"},
        (-8.544355, -172.5099): {"country": "Tokelau", "port_name": "Atafu"},
        (-9.38471, -171.2497): {"country": "Tokelau", "port_name": "Fakaofo"},
        (-9.173953, -171.8198): {"country": "Tokelau", "port_name": "Nukunomu"},
        (-21.33943, -174.9553): {"country": "Tonga", "port_name": "Eua Island"},
        (-18.66332, -173.9837): {"country": "Tonga", "port_name": "Neiafu"},
        (-21.13478, -175.1914): {"country": "Tonga", "port_name": "Nuku Alofa"},
        (-19.80511, -174.3529): {"country": "Tonga", "port_name": "Tonga"},
        (-8.515751, 179.1826): {"country": "Tuvalu", "port_name": "Funafuti"},
        (-20.23727, 169.7782): {"country": "Vanuatu", "port_name": "Aneityum"},
        (-16.25447, 167.9247): {"country": "Vanuatu", "port_name": "Craig Cove"},
        (-15.09245, 168.0869): {"country": "Vanuatu", "port_name": "Maewo"},
        (-17.73969, 168.3062): {"country": "Vanuatu", "port_name": "Port Vila"},
        (-15.506, 167.18): {"country": "Vanuatu", "port_name": "Santo"},
        (-14.29566, -178.1595): {"country": "Wallis Futuna Is", "port_name": "Futuna Island"},
        (-13.28155, -176.1739): {"country": "Wallis Futuna Is", "port_name": "Mata Utu"},
        (-13.33952, -176.197): {"country": "Wallis Futuna Is", "port_name": "Wallis Island Apt"},
        (-20.91877, 167.2787): {"country": "New Caledonia", "port_name": "Lifou"},
        (-20.71581, 166.4188): {"country": "New Caledonia", "port_name": "Mouly"},
        (-17.50382, -149.8561): {"country": "French Polynesia", "port_name": "Opunohu Bay"},
        #new
        (13.1527, 100.9310): {"country": "Thailand", "port_name": "Sri Racha"},
        (14.7950, 120.2719): {"country": "Philippines", "port_name": "Subic Bay"},
        (22.3193, 114.1694): {"country": "Hong Kong", "port_name": "Hong Kong"},
        (22.7654, 113.6054): {"country": "China", "port_name": "Nansha"},
        (29.8683, 121.5440): {"country": "China", "port_name": "Ningbo"},
        (31.2304, 121.4737): {"country": "China", "port_name": "Shanghai"},
        (31.6460, 120.7422): {"country": "China", "port_name": "Changshu"},
        (36.0671, 120.3826): {"country": "China", "port_name": "Qingdao"},
        (39.0076, 117.7107): {"country": "China", "port_name": "Xingang (Tianjin)"},
        (35.1796, 129.0756): {"country": "South Korea", "port_name": "Busan"},
        (33.5902, 130.4017): {"country": "Japan", "port_name": "Hakata (Fukuoka)"},
        (34.5600, 131.0400): {"country": "Japan", "port_name": "Chofu"},
        (33.9431, 130.9575): {"country": "Japan", "port_name": "Moji"},
        (34.6937, 135.5023): {"country": "Japan", "port_name": "Osaka"},
        (34.6901, 135.1955): {"country": "Japan", "port_name": "Kobe"},
        (35.1815, 136.9066): {"country": "Japan", "port_name": "Nagoya"},
        (35.4437, 139.6380): {"country": "Japan", "port_name": "Yokohama"},
        (26.5013, 127.9454): {"country": "Japan", "port_name": "Okinawa"},
        (3.0000, 101.4000): {"country": "Malaysia", "port_name": "Port Klang"},
        (1.3667, 103.5333): {"country": "Malaysia", "port_name": "Tanjung Pelepas"},
        (1.3521, 103.8198): {"country": "Singapore", "port_name": "Singapore"},
        (-6.2088, 106.8456): {"country": "Indonesia", "port_name": "Jakarta"},
        (-7.2575, 112.7521): {"country": "Indonesia", "port_name": "Surabaya"},
        (-19.2589, 146.8169): {"country": "Australia", "port_name": "Townsville"},
        (-23.8426, 151.2519): {"country": "Australia", "port_name": "Gladstone"},
        (-27.4698, 153.0251): {"country": "Australia", "port_name": "Brisbane"},
        (-33.8688, 151.2093): {"country": "Australia", "port_name": "Sydney"},
        (-32.9283, 151.7817): {"country": "Australia", "port_name": "Newcastle"},
        (-37.8136, 144.9631): {"country": "Australia", "port_name": "Melbourne"},
        (-35.8416, 174.4744): {"country": "New Zealand", "port_name": "Marsden Point"},
        (-36.8485, 174.7633): {"country": "New Zealand", "port_name": "Auckland"},
        (-37.6380, 176.1810): {"country": "New Zealand", "port_name": "Mount Maunganui"},
        (-39.4928, 176.9120): {"country": "New Zealand", "port_name": "Napier"},
        (-41.2706, 173.2840): {"country": "New Zealand", "port_name": "Nelson"},
        (-41.2865, 174.7762): {"country": "New Zealand", "port_name": "Wellington"},
        (-43.6000, 172.7200): {"country": "New Zealand", "port_name": "Lyttelton"},
        (-44.3967, 171.2556): {"country": "New Zealand", "port_name": "Timaru"},
        (21.3069, -157.8583): {"country": "USA", "port_name": "Honolulu"},
        (34.0522, -118.2437): {"country": "USA", "port_name": "Los Angeles"},
        (37.8044, -122.2711): {"country": "USA", "port_name": "Oakland"},
        (47.6062, -122.3321): {"country": "USA", "port_name": "Seattle"},
        (49.2827, -123.1207): {"country": "Canada", "port_name": "Vancouver"},
        (8.9824, -79.5199): {"country": "Panama", "port_name": "Panama City"},
        #new new ports

        (31.7635,120.9466): {"country": "China", "port_name": "Changshu 2"},
        (35.10162, 129.036): {"country": "South Korea", "port_name": "Busan 2"},
        (34.61406, 135.4404): {"country": "Japan", "port_name": "Osaka 2"},
        (35.046, 136.836): {"country": "Japan", "port_name": "Nagoya 2"},
        (1.259366, 103.7544): {"country": "Singapore", "port_name": "Singapore 2"},
        (-6.125718, 106.8512): {"country": "Indonesia", "port_name": "Jakarta 2"},
        (33.74021, -118.265): {"country": "USA", "port_name": "Los Angeles 2"},
        (22.58425, 120.3181): {"country": "Taiwan", "port_name": "Kaohsiung"},
        (33.75493, -118.2143): {"country": "USA", "port_name": "Long Beach"},

    }

    # Get the country and port name from the dictionary
    port_data = port_info.get((lat_port, lon_port), {})
    if not port_data:
        print(f"Port information not found for lat={lat_port}, lon={lon_port}.")
        return

    country = port_data["country"]
    port_name = port_data["port_name"]

    # Generate file name based on the port data and date range
    output_file = f"{country}_{port_name}_{start_date}_{end_date}.xlsx"

    # Convert data to DataFrame
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["uuid"], keep="first", inplace=True)

    # Save to a new Excel file
    with pd.ExcelWriter(output_file, mode="w", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Location Filter Data", index=False)
    print(f"Data saved to {output_file}.")

# Modify generate_port_report to pass lat_port, lon_port, start_date, and end_date to save_to_excel
def generate_port_report(lat_port, lon_port, radius, start_date, end_date):
    report_ids = submit_report_request(lat_port, lon_port, radius, start_date, end_date)
    if not report_ids:
        print("No reports generated.")
        return

    all_vessels = []
    for report_id in report_ids:
        # Check the status with retries and timeout
        download_url = check_report_status(report_id)
        if not download_url:
            print(f"Report ID {report_id} failed or not ready after timeout.")
            continue
        
        # Process the report if ready
        vessels = download_report_data(download_url)
        for vessel in vessels:
            all_vessels.append({
                "uuid": vessel.get("uuid"),
                "report_id": report_id  # Add the report_id to the vessel's data
            })

    if all_vessels:
        save_to_excel(all_vessels, lat_port, lon_port, start_date, end_date)
    else:
        print("No vessel data to save.")


if __name__ == "__main__":
    coordinates_with_radius = [
        (31.7635,120.9466,4),
        (35.10162, 129.036,4),
        (34.61406, 135.4404,4),
        (35.046, 136.836,4),
        (1.259366, 103.7544,4),
        (-6.125718, 106.8512,4),
        (33.74021, -118.265,4),
        (22.58425, 120.3181,4),
        (33.75493, -118.2143,4),
    ]

    
    months = [
        ("2024-01-01", "2024-01-31"),
        ("2024-02-01", "2024-02-29"),
        ("2024-03-01", "2024-03-31"),
        ("2024-04-01", "2024-04-30"),
        ("2024-05-01", "2024-05-31"),
        ("2024-06-01", "2024-06-30"),
        ("2024-07-01", "2024-07-31"),
        ("2024-08-01", "2024-08-31"),
        ("2024-09-01", "2024-09-30"),
        ("2024-10-01", "2024-10-31"),
        ("2024-11-01", "2024-11-30"),
        ("2024-12-01", "2024-12-31")
    ]
    
    for lat_port, lon_port, radius in coordinates_with_radius:
        print(f"Processing reports for port at lat: {lat_port}, lon: {lon_port}, radius: {radius} nautical miles")
        for start_date, end_date in months:
            print(f"Generating report for {start_date} to {end_date}")
            start_time = time.time()
            generate_port_report(lat_port, lon_port, radius, start_date, end_date)
            elapsed_time = time.time() - start_time
            print(f"Execution time for {start_date} to {end_date}: {elapsed_time:.2f} seconds")


#can probably do a for loop and big dictionary with port coordinates! no need for direct code connection
#can have separate excels for each port (maybe useful later - because then can group into countries and write a code to compare duplicates and get domestic!!!!
#for this might need to adjust excel saving funtion, make it create an excel every time with name of port!

#47fb083c-77e6-e803-61b7-c2a6fd985d7e check this one, both in papeete and suva in jan - maybe it moved?