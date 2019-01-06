#!/usr/bin/python3
# CRA OCAD Project
# 
# LatLongGenerator.py 
# Created for group project: 
# Andrew Campbell, Xiang Gao, Gurleen Kaur and Apurv Shah
# Algonquin College
# Date: Mar 29, 2018
# Input: File with postal codes, File with Lat/Long Mappings
# Output: Postal Code, Latitude, Longitude
#
# Process: Loop through all postal codes and lookup the lat/long. 
# Write all this to an output file. 

import pandas as pd
import os
import googlemaps

# Google Maps API Key
key = "Enter key here"
gmaps = googlemaps.Client(key)


def gmap_lookup(postalCode):
    
    # Try looking up Lat/Long from Google Maps Geo-Coding API
    print(postalCode + ' lookup being done with Google Maps')
            
    geocode_result = gmaps.geocode(postalCode+', Canada')[0]
    lat  = geocode_result["geometry"]["location"]["lat"]
    long = geocode_result["geometry"]["location"]["lng"]

    # Check to see if Gmaps returned a null value
    # Null value is encoded as: (56.130366, -106.346771) 
    # eg. this happens for E1C0T5
    epsilon = 0.000001
    latDiff  = abs(lat  - 56.130366)
    longDiff = abs(long + 106.346771)
                        
    # Need to use this for floating point compare 
    if (latDiff < epsilon and longDiff < epsilon):
        gotResult = 0
    else:
        gotResult = 1
        
    return (gotResult, lat, long)


def generate_lat_long(directory, filename, lat_lookup, long_lookup):
    print('Working on.... ' + filename)

    # Read the source
    df = pd.read_csv(directory+'/'+filename, header=0)
    
    # Convert the postal code column to a list
    postalCodeList = df['Postal Code'].tolist()

    locationList = []
    
    # Loop through all postal codes
    for pc in postalCodeList:
        
        # The following two postal codes need to modified slightly to get 
        # the correct lookup
        #A1E0G5 -> A1E0B9
        #V3Z9R6 -> V3S9R2
        if (pc == "A1E0G5"):
            postalCode = "A1E0B9"
        elif (pc == "V3Z9R6"):
            postalCode = "V3S9R2" 
        else:
            postalCode = pc       
        
        gotResult = 0 
        # Lookup Lat/Long based on values from the CSV
        if postalCode in lat_lookup: 
            lat  = lat_lookup[postalCode]
            long = long_lookup[postalCode]
            gotResult = 1
                         
        # Try looking up Lat/Long from Google Maps Geo-Coding API
        if (gotResult is 0): 
            (gotResult, lat, long) = gmap_lookup(postalCode)
            
        # Try looking up Lat/Long from Google Maps Geo-Coding API
        # Using FSA (first 3 char of postal code)
        if (gotResult is 0): 
            (gotResult, lat, long) = gmap_lookup(postalCode[:3])
                        
        if (gotResult is 1): 
            locationList.append((pc, lat, long))
        else:
            print("***ERROR***: Did not find lat/long for ", postalCode)

    # Write the data to a new CSV to allow comparision
    final_labels = ['PostalCode', 'Latitude', 'Longitude']    
    final_df = pd.DataFrame.from_records(locationList, columns=final_labels)
    final_df.set_index('PostalCode', inplace=True)
    final_df.to_csv('2_LatLongLists/' + filename)
    print('Done with.... ' + filename)


def main_program():
    
    # Load postal code lookup csv into a pandas dataframe
    pc_df = pd.read_csv('1_PostalCodes/CanadianPostalCodes.csv', header=0)
    pc_df.set_index('PostalCode', inplace=True)

    # Covert the data frame to a dictionary
    pc_lookup = pc_df.to_dict()
    lat_lookup  = pc_lookup['Latitude']
    long_lookup = pc_lookup['Longitude']
    
    directory = '1_StartFiles'
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        generate_lat_long(directory, filename, lat_lookup, long_lookup)
    
main_program()

