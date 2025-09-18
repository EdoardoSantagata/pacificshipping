# pacificshipping
This toolkit performs 3 functions for analysis of the decarbonisation of the maritime shipping sector in Pacific Island Countries and Territories (PICTs):  
(Function 1) Maps shipping routes based on operator schedules and assesses connectivity levels  
(Function 2) Extracts vessel parameters for a selection of ports, including key characteristics, operational days at sea, and average annual speed  
(Function 3) Analyses decarbonisation scenarios for a selected fleet with estimation of annual fuel requirements, operational costs, emissions, and added renewable energy capacity.  

There toolkit consists of the following packages, categorised by function:  
(Function 1 - Route mapping and connectivity)  
(1) pacificshipping.py - this analyses service routes and maps them using a sea routing algorithm for relevant sections. provides 2 main outputs: "pacificshippingmap.html", which shows the shipping network categorised by operator; "DENSITY.html", which shows a simplified polyline network with segment densities proportional to the amount of service routes passing through those segments  
(Function 2 - Database derivation)  
(2) shippinganalysis.py - statistics, database inspector, ship fuel consumption estaimtes, scenario analysis  
(3) portcalculator.py - calculates distances between ports and anchorages, and gives coordinates for all ports  
(4) checkports.py - checks if ports exist near specific coordinates , required to inspect particular problematic areas  
(5) apilocation.py - obtains reports for specified timeframe and coordinates to see all ships that have passed through there. also gives raw report data.  
(6) apistuff.py - returns operational days and so forth to augment the pacific_shipping_database.xlsx. also outputs movements for each ship specified  
(7) databaseworker.py - sorts through pacific_shipping_database.xlsx info obtained via filter options in marinetraffic (requires manual input of raw data)  
(8) mappingships.py - maps ships based on route outputted in api folder from apistuff.py  
(Function 3 - Decarbonisation scenario analysis)  
(X) XXX  
