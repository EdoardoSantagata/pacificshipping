# Pacific Shipping Toolkit

(currently being updated - all files back online soon)

An open-source toolkit for mapping shipping routes, deriving regional vessel databases, and modelling decarbonisation scenarios for maritime shipping in Pacific Island Countries and Territories (PICTs).

This toolkit accompanies the following publications:

- Santagata, E. 2026. *Planning Frameworks and Tools for Secure and Resilient Clean Energy Transitions in Pacific Island Countries and Territories.* PhD Thesis, UNSW Sydney. DOI: https://doi.org/10.26190/unsworks/31988
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

This function combines two data acquisition methods — a location-based filtering method (MarineTraffic) and an API-based method (Datalastic) — to derive a consolidated database of vessels operating in PICT waters. Together, the scripts constitute a structured pipeline to extract and validate API-based vessel data, carry out systematic filtering and deduplication, estimate missing vessel attributes via regression models, and estimate annual fuel/energy consumption.

The scripts are designed to work with MarineTraffic (Enterprise Plan) and Datalastic (Developer Pro Plan) data formats and API endpoints. The combined dataset is cross-checked against operator schedules, yielding a final regional fleet of approximately 4,000 commercial passenger and cargo vessels.

### Port validation and preparation

#### `portcalculator.py`

Calculates distances between ports and anchorages and provides coordinates for all ports considered in the study. Used to calibrate the search radii applied in the API-based database derivation method. Radii are dynamically adjusted based on the distance to the nearest anchorage (scaled by a factor of 1.5), with manual overrides for ports with improperly recorded anchorage coordinates (e.g. Nuku'alofa, Tonga).

#### `checkports.py`

Validates whether ports exist near specific coordinates against the API. Used to inspect and resolve problematic areas in maritime datasets where port locations may be inaccurate or ambiguous.

### Data acquisition

#### `databaseworker.py`

Processes raw vessel data obtained via MarineTraffic's location-based filtering. Implements sequential filtering by port, flag, and vessel type before consolidating records across MarineTraffic sheets and operator fleet lists. Filters are applied based on:
- Destination Port Country in PICTs
- Current Port Country in PICTs
- Origin Port Country in PICTs
- Previous to Origin Port Country in PICTs

Requires manual input of raw data exported from MarineTraffic into `pacific_shipping_database.xlsx`. Only commercial, non-fishing vessels for passenger and cargo operations are retained; fishing vessels, tugs, patrol vessels, pleasure craft, and similar vessel types are excluded.

#### `apilocation.py`

Queries the Datalastic API to identify vessels that passed through specified coordinates within a given timeframe. Port coordinates for 57 major PICT ports are used as scan points. Also provides raw report data for further analysis.

#### `apistuff.py`

Augments the vessel database with operational parameters. Uses vessel IMO or MMSI numbers to query the Datalastic API for annual operational days at sea and average speed throughout 2024. For Class B transponder vessels or those without an IMO number, operational parameters are assumed based on vessel type averages. Also outputs movement records for each specified vessel.

#### `uuiduser.py`

Queries vessel UUIDs directly via the Datalastic API, returning structured vessel attributes including flag, gross tonnage, deadweight tonnage, dimensions, draught, speed, and build year. These attributes are appended to the working database to enrich records obtained from the other acquisition methods.

### Deduplication and consolidation

#### `duplicatecheck.py`

Flags and removes duplicate entries from the merged MarineTraffic and Datalastic datasets by matching on IMO or MMSI identifiers. Reports unresolved duplicates for manual inspection. This is a critical step as vessels may appear in both data sources or across multiple filtering criteria.

### Analysis and visualisation

#### `shippinganalysis.py`

Central analysis tool implemented as a multi-page Dash application. Provides:
- **Vessel categorisation** across detailed, generic, simplified, and contextual groupings
- **Missing parameter estimation** — estimates missing DWT values via regression models and group averages, using a prioritisation framework that selects the appropriate regression approach based on which vessel properties are available. For vessel types with unique physical characteristics (e.g. passenger vessels), type-specific regression models are used.
- **Fuel consumption estimation** — calculates annual specific fuel consumption (SFC) using the empirical formula from Barrass (2004), with conversion to energy values using fuel-type-specific energy densities
- **Emissions inventory** — integrates emission intensities and fuel allocation assumptions by vessel type
- **Statistical summaries and database inspection**

#### `mappingships.py`

Maps individual vessel tracks from AIS coordinate data output by `apistuff.py`. Filters and normalises coordinate data to account for unrealistic jumps, repeated points, and crossings at the International Date Line. Enables comparison of actual vessel movements with the mapped operator service lines from Function 1.

**Dependencies (Function 2):** `pandas`, `numpy`, `openpyxl`, `requests`, `geopy`, `plotly`, `dash`, `dash_table`, `scikit-learn`, `math`, `collections`

---

## Function 3 — Decarbonisation Scenario Analysis

The scenario modelling tool is provided as an **Excel spreadsheet** included in the repository. The spreadsheet contains the modelling framework for assessing decarbonisation pathways — users populate it with their own fleet data and scenario parameters. Dummy vessel data is included in the spreadsheet to demonstrate functionality; the database can be populated with real data by running the database derivation scripts in Function 2, or with data derived from external sources provided the input follows the format specified in the `raw` sheet.

The tool supports the development of both normative and exploratory scenarios. In the associated publications, 10 scenarios were modelled (5 normative derived from IMO, IEA, IRENA, and PBSP targets; 5 exploratory stress-testing alternative energy futures), though these specific scenario configurations are not pre-built into the spreadsheet.

### Decarbonisation measures supported

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

---

## Data and Licensing

**Software:** This toolkit is released under the [MIT License](LICENSE).

**Data:** Raw vessel data extracted from MarineTraffic and Datalastic is **not** included in this repository in accordance with their respective user agreements. Users wishing to derive their own maritime shipping database can subscribe to these services to access the required raw data. The authors declare no commercial or financial relationship with these data providers.

---

## Requirements

- Python 3.x
- Key Python dependencies and standard data science libraries (see below)
- Microsoft Excel (for the scenario analysis tool)
- Access to MarineTraffic (Enterprise Plan) and/or Datalastic (Developer Pro Plan) for database derivation

### Python dependencies

**Route mapping (Function 1):**
`searoute`, `folium`, `selenium`

**Database derivation (Function 2):**
`pandas`, `numpy`, `openpyxl`, `requests`, `geopy`, `plotly`, `dash`, `dash_table`, `scikit-learn`

---

## Citation

If you use this toolkit in your research, please cite:

> Santagata, E. 2026. *Planning Frameworks and Tools for Secure and Resilient Clean Energy Transitions in Pacific Island Countries and Territories.* PhD Thesis, UNSW Sydney. DOI: https://doi.org/10.26190/unsworks/31988

This citation requirement will be updated once the associated thesis chapter is published in a peer-reviewed journal.

---

## Contact

For questions or collaboration enquiries, please open an issue on this repository or contact the corresponding author (edoardo.santagata@unsw.edu.au)
