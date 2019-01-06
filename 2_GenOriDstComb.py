#!/usr/bin/python3
# CRA OCAD Project
# 
# GenOriDstComb.py 
# Created for group project: 
# Andrew Campbell, Xiang Gao, Gurleen Kaur and Apurv Shah
# Algonquin College
# Date: Mar 23, 2018
# This file generates the origin and destination combinations
# for the driving distances calculations between postal codes. 
# This file also calculates the Line of Sight Distance (LOSD) between
# all origin and destination combinations.  

# Trick 1: Look up Lat/Long before doing combolist to reduce 
# the number of lat/long lookups. Effectively, we are creating 
# a cache of data which speeds things up

import itertools
import pandas as pd
import os
import datetime
from geopy.distance import vincenty

def calculate_losd(comboList, lat_lookup, long_lookup):    
    print ("Starting LOSD Calculations. Time: " 
           + str(datetime.datetime.now().strftime('%H:%M:%S'))) 
     
    losdList = []
    i = 0
    
    # Iterate through the list of combinations of origins and destinations
    for combo in comboList:

        if (i%1000 is 0):
            print(str(i) + ". Time: " 
                  + str(datetime.datetime.now().strftime('%H:%M:%S')))
        i+=1
                
        origin = combo[0]
        dest   = combo[1]

        # Get Lat/Long     
        oriLat = lat_lookup[origin]
        oriLng = long_lookup[origin]
        dstLat = lat_lookup[dest]
        dstLng = long_lookup[dest]
    
        # Get the Line of Sight Distance (LOSD) between origin(latitude,longitude)
        # and destination(latitude,longitude)           
        losd = vincenty((oriLat, oriLng), 
                        (dstLat, dstLng)).kilometers
        
        losdList.append((origin, dest, round(losd), oriLat, oriLng, dstLat, dstLng))
        
    return losdList

def generate_combinations(directory, filename):
    print('Working on.... ' + filename)

    ll_dir = '2_LatLongLists'
    
    # Read the source
    df = pd.read_csv(directory+'/'+filename, header=0)
    
    # Read the lookup lists
    lat_lng_df = pd.read_csv(ll_dir+'/'+filename, header=0)
    lat_lng_df.set_index('PostalCode', inplace=True)

    # Covert the lookup data frame to a dictionary
    ll_lookup = lat_lng_df.to_dict()
    lat_lookup  = ll_lookup['Latitude']
    long_lookup = ll_lookup['Longitude']
    
    # Convert the postal code column to a list
    postalCodeList = df['Postal Code'].tolist()
    
    # Create a new list with all the combinations 
    comboList = list(itertools.combinations(postalCodeList, 2))

    # Calculate Line of Sight    
    losdList = calculate_losd(comboList, lat_lookup, long_lookup)

    # Sort the list 
    losdList.sort(key=lambda tup: tup[2])

    # Create a Pandas Dataframe
    final_labels = ['Origin', 'Destination', 'LOSD', 
                    'OriLat', 'OriLng', 
                    'DstLat', 'DstLng']    
    final_df = pd.DataFrame.from_records(losdList, columns=final_labels)
    
    # LOSD of 0 is updated to 1 as you may have atleast 1 km to drive
    # Note this will have negligible effect on the overall result
    final_df = final_df.replace(0, 1)
    
    # Calculate Aggregates
    avg = round(final_df['LOSD'].mean())
    total = final_df['LOSD'].sum()
    cnt = len(final_df)
    print(filename, avg, total, cnt)
    
    # Write the data to a new CSV to allow comparision
    final_df.set_index('Origin', inplace=True)
    final_df.to_csv('3_ComboLists/' + filename)
    print('Done with.... ' + filename)

    return (filename, avg, total, cnt)

def main_program():
    directory = '1_StartFiles'

    results = []

    for filename in os.listdir(directory):
        result = generate_combinations(directory, filename)
        results.append(result)
    
    for result in results:
        print(result)
    
main_program()

