Purpose of the Algorithm
========================
For a list of postal codes, caculate the driving distance between each and every postal code in the file. Each file will be treated independently allowing a region to be identified per file. From this a travel cost estimate will be calculated per region. For driving distances above 300 km, a flight cost will be calculated. Linear regression is used to reduce the number of driving distance lookups required.   


Instructions for running the python script 
==========================================
The following folders will need to be created:
1. 3_ComboLists
2. 4_CostLists
3. 5_FinalLists

Libraries will need to be installed using the following process: 
1. Start command window with Admin privileges 
2. pip install <library name>
3. Libraries required include pandas, googlemaps, geopy


Details Regarding Algorithm
===========================

Phase 1 - provides a baseline model based on Line of Sight Calculations (straight line distance). 
Phase 2 - improve the accuracy of model based on actual driving distance calculations
LOSD over 300 km => train or plane will be used for travel which does not require driving distance lookups.

By splitting the algorithm into two phases, a 42% reduction was achieved in the total number of driving distance lookups required. 

Phase 1 gave the Line of Sight Distance for all records (approximately one million). However, there were still around 500,000 records for which the driving distance lookup would be required. Only 2500/lookups were possible per day through the Google Distance Matrix Application Programming Interface (API). To solve this issue, a linear regression model was used to approximate the driving distance from the line of sight distance. 

Driving Distance Approximation = Multiplier per region * LOSD

See attached diagram (jpg file) for a high level overview of the algorithm.