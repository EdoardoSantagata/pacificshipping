# pacificshipping
Tool to track shipping routes and model decarbonisation scenarios in the Pacific.

There are 3 main applications in this tool pack:
(1) pacificshipping.py - this analyses service routes and maps them using a sea routing algorithm for relevant sections. provides 2 main outputs: "pacificshippingmap.html", which shows the shipping network categorised by operator; "DENSITY.html", which shows a simplified polyline network with segment densities proportional to the amount of service routes passing through those segments
(2) shippinganalysis.py - statistics, database inspector, ship fuel consumption estaimtes, scenario analysis
(3) portcalculator.py - calculates distances between ports and anchorages, and gives coordinates for all ports
(4) checkports.py - checks if ports exist near specific coordinates , required to inspect particular problematic areas
(5) apilocation.py - obtains reports for specified timeframe and coordinates to see all ships that have passed through there. also gives raw report data.
(6) apistuff.py - returns operational days and so forth to augment the pacific_shipping_database.xlsx. also outputs movements for each ship specified
(7) databaseworker.py - sorts through pacific_shipping_database.xlsx info obtained via filter options in marinetraffic (requires manual input of raw data)
(8) mappingships.py - maps ships based on route outputted in api folder from apistuff.py
