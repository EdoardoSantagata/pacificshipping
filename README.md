# Pacific Shipping Toolkit

(currently being updated - all files back online soon)

An open-source toolkit for mapping shipping routes, deriving regional vessel databases, and modelling decarbonisation scenarios for maritime shipping in Pacific Island Countries and Territories (PICTs).

This toolkit accompanies the following publications:

- Santagata, E. 2026. *Planning Frameworks and Tools for Secure and Resilient Clean Energy Transitions in Pacific Island Countries and Territories.* PhD Thesis, UNSW Sydney.
- Santagata, E., MacGill, I., Raturi, A., Bruce, A. *Decarbonising maritime shipping in Pacific Island Countries and Territories (PICTs) — an overview and regional database to support energy planning.* Submitted to Journal of Ocean Engineering and Science (currently under review)

## Overview

The toolkit performs three core functions:

1. **Route Mapping and Connectivity** — Maps shipping routes based on operator schedules for 14 principal carriers servicing 20 PICTs, and assesses connectivity using established metrics.
2. **Database Derivation and Fuel Consumption Estimation** — Extracts vessel parameters from maritime data providers, derives a consolidated regional fleet database, and estimates specific fuel consumption for the fleet.
3. **Decarbonisation Scenario Analysis** — Models normative and exploratory scenarios for clean shipping transitions, estimating future energy demands, emissions, costs, and renewable energy capacity requirements.

Functions 1 and 2 are implemented as Python scripts. Function 3 is implemented in an Excel-based modelling tool.

---

## Function 1 — Route Mapping and Connectivity

### `servicemapping.py`

Maps shipping service routes and assesses regional connectivity. Operator schedules from 14 carriers are processed and routes are derived using the orthodromic routing algorithm via the [`searoute`](https://github.com/eurostat/searoute) Python package, which computes the shortest sea path while avoiding land masses and respecting navigational constraints. Routes crossing the International Date Line (e.g. to the US West Coast) are handled separately due to limitations in current routing databases.

**Outputs:**
- `pacificshippingmap.html` — interactive map of the shipping network, categorised by operator
- `DENSITY.html` — simplified polyline network showing segment densities proportional to the number of service routes passing through each segment

**Connectivity metrics calculated** (per de Langen et al., 2016):
- Port frequency
- Route count
- Number of unique country connections
- Number of service providers

Results can be compared with existing regional maps (e.g. World Bank, 2023) to identify improvements in resolution and route-level detail.

---

## Function 2 — Database Derivation and Fuel Consumption

This function combines two data acquisition methods — a location-based filtering method (MarineTraffic) and an API-based method (Datalastic) — to derive a consolidated database of vessels operating in PICT waters. The scripts in this function are designed to work with MarineTraffic (Enterprise Plan) and Datalastic (Developer Pro Plan) data formats and API endpoints.

### `databaseworker.py`

Processes raw vessel data obtained via MarineTraffic's location-based filtering. Filters are applied based on:
- Destination Port Country in PICTs
- Current Port Country in PICTs
- Origin Port Country in PICTs
- Previous to Origin Port Country in PICTs

The script sorts and processes the `pacific_shipping_database.xlsx` file, which requires manual input of raw data exported from MarineTraffic. Only commercial, non-fishing vessels for passenger and cargo operations are retained; fishing vessels, tugs, patrol vessels, pleasure craft, and similar vessel types are excluded.

### `apilocation.py`

Queries the Datalastic API to identify vessels that passed through specified coordinates within a given timeframe. Port coordinates for 57 major PICT ports are used as scan points, with search radii dynamically adjusted based on the distance to the nearest anchorage (scaled by a factor of 1.5). Radii for ports with improperly recorded anchorage coordinates (e.g. Nuku'alofa, Tonga) are set manually based on visual inspection via MarineTraffic. Also provides raw report data for further analysis.

### `apistuff.py`

Augments the vessel database with operational parameters. Uses vessel IMO or MMSI numbers to query the Datalastic API for annual operational days at sea and average speed throughout 2024. For Class B transponder vessels or those without an IMO number, operational parameters are assumed based on vessel type averages. Also outputs movement records for each specified vessel.

### `portcalculator.py`

Calculates distances between ports and anchorages, and provides coordinates for all ports considered in the study. Used to calibrate the search radii applied in the API-based database derivation method.

### `checkports.py`

Checks whether ports exist near specific coordinates. Used to inspect and validate problematic areas in the maritime datasets where port locations may be inaccurate or ambiguous.

### `shippinganalysis.py`

Central analysis script that serves as the main dashboard for the database. Provides:
- Statistical summaries and visualisation of the regional fleet
- Database inspection and validation tools
- Specific fuel consumption (SFC) estimation using the empirical formula from Barrass (2004)

SFC estimation uses a prioritisation framework to handle missing vessel parameters through statistical regression, leveraging physical relationships between vessel volume, carrying capacity, length, and draught. For certain vessel types with unique physical characteristics (e.g. passenger vessels), type-specific regression models are used. Fuel consumption values are converted to energy values using fuel-type-specific energy densities, with fuel type assumed based on vessel type where direct information is unavailable.

### `mappingships.py`

Maps individual vessel routes based on movement data output from `apistuff.py`. Generates visual representations of vessel tracks for validation and analysis, enabling comparison with mapped operator routes from Function 1.

---

## Function 3 — Decarbonisation Scenario Analysis

The scenario modelling tool is implemented as an **Excel spreadsheet** included in the repository. It models 10 scenarios — 5 normative and 5 exploratory — to assess different decarbonisation pathways for the regional PICT shipping fleet.

### Scenarios

**Normative scenarios** (1–5) are derived from targets and studies by the IMO (2023 GHG Strategy), IEA (Net Zero), IRENA (1.5°C pathway), and the Pacific Blue Shipping Partnership (PBSP). They are adapted with slight variability to distinguish pathways and should be understood as derived rather than exact reproductions.

**Exploratory scenarios** (6–10) stress-test alternative energy futures with varied uptake of clean fuels and operational measures.

### Decarbonisation measures modelled

- **Operational measures:** slow steaming (SS), hull coating and propeller upgrades (HCP), sailing and hybrid technologies (SH)
- **Clean fuels:** green hydrogen, e-ammonia, e-methanol, bio-LNG, bio-ethanol, HVO, synthetic diesel, battery-electric

### Modelling approach

Transitions are modelled using logistic (S-curve) functions parameterised by adoption rate (*k*) and inflection point (*t₀*), reflecting typical technology deployment curves. For each vessel type, proportions are allocated to determine clean fuel conversion pathways and suitability for operational measures.

### Outputs per scenario

- Annual fuel consumption by type
- Emissions (well-to-wake basis)
- Operational costs
- Required renewable electricity capacity for clean fuel production
- IMO carbon levy impacts for the regional fleet

The spreadsheet can work with data derived from Function 2 or from external sources, provided the input follows the format specified in the `raw` sheet.

---

## Data and Licensing

**Software:** This toolkit is released under the [MIT License](LICENSE).

**Data:** Raw vessel data extracted from MarineTraffic and Datalastic is **not** included in this repository in accordance with their respective user agreements. Users wishing to derive their own maritime shipping database can subscribe to these services to access the required raw data. The authors declare no commercial or financial relationship with these data providers.

---

## Requirements

- Python 3.x
- Key Python dependencies include: `searoute`, `folium`, `pandas`, `numpy`, `requests`, and standard data science libraries
- Microsoft Excel (for the scenario analysis tool)
- Access to MarineTraffic (Enterprise Plan) and/or Datalastic (Developer Pro Plan) for database derivation

---

## Citation

If you use this toolkit in your research, please cite:

> Santagata, E. 2026. *Planning Frameworks and Tools for Secure and Resilient Clean Energy Transitions in Pacific Island Countries and Territories.* PhD Thesis, UNSW Sydney.

This citation requirement will be updated once the associated thesis chapter is published in a peer-reviewed journal.

---

## Contact

For questions or collaboration enquiries, please open an issue on this repository or contact the corresponding author (edoardo.santagata@unsw.edu.au)
