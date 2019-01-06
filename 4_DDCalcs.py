#!/usr/bin/python3
# CRA OCAD Project
# 
# DDCalcs.py
# Created for group project: 
# Andrew Campbell, Xiang Gao, Gurleen Kaur and Apurv Shah
# Algonquin College
# Date: Mar 30, 2018
# This file calculates the cost for the Driving Distance between
# all origin and destination combinations using the Google Maps API.
# The Google Maps API only allows for 2500 lookup every day. 
# However, we need to do 500K lookups. 
#
# If desired, all 500K lookups can be calculated. However, we can 
# get very close to the final model using an approximation factor.
# The formula is as follows:
# Approx. Driving distance = Multiplication Factor X LOSD Distance
# 
# There are 5 regions, and the lookups are split according to the 
# number of records per region:
# Atlantic :  250
# ON-NU    : 1000
# Pacific  :  500
# Prairie  :  250
# Quebec   :  500
# 
# Based on the lookups done, we can calculate a multiplication factor. 
# With each iteration, the multiplication factor will become more accurate
# and start converging. 

import os
import datetime
import googlemaps
import pandas as pd
from random import randint

# Google Distance Matrix API
key = "Enter key here"

gmaps = googlemaps.Client(key)

def do_lookups(directory, filename):
    print('Working on.... ' + filename)

    # Do a fixed number of lookups per file
    if 'Atlantic' in filename:
        lookupsMax =  700
    elif 'Ontario' in filename:
        lookupsMax =  500
    elif 'Pacific' in filename:
        lookupsMax =  500
    elif 'Prairie' in filename:
        lookupsMax =  250
    elif 'Quebec' in filename:
        lookupsMax =  500
    else:
        lookupsMax =    0

    lookupsDone = 0 

    # Read the source
    df = pd.read_csv(directory+'/'+filename, header=0)

    # Find the index of the entry with the first 300km LOSD
    # Above this index, is the range on which we want to perform the 
    # driving distance calcs
    maxIndex = df['LOSD'].searchsorted(300, side='left')[0]    

    # Every incremental run will result in the Update Version to be incremented
    updateIncr = df['Update'].max() + 1
    
    i = 1
    # Update randomly selected entries wtih the driving distance for 
    # the max number of lookups for the region
    while lookupsDone < lookupsMax:
        # Randomly select between 0 and entries with LOSD < 300
        idx = randint(0, maxIndex-1)

        # If update is 0, then update the driving distance by doing a lookup 
        if (df.loc[idx, 'Update'] == 0):
            ## Update drving distance after doing a lookup
            distance = gmaps.distance_matrix(origins = 
                                             str(df.loc[idx, 'OriLat'])+', '+
                                             str(df.loc[idx, 'OriLng']),
                                             destinations=
                                             str(df.loc[idx, 'DstLat'])+', '+
                                             str(df.loc[idx, 'DstLng']), 
                                             mode='driving')  
            
            # There are some places that don't have roads in Google Maps
            # For these locations, just skip as we can use the multiplier
            if (distance['rows'][0]['elements'][0]['status'] != 'ZERO_RESULTS'):            
                dist_km = round(distance['rows'][0]['elements'][0]['distance']['value']/1000)                                                                

                # Same as LOSD, 0 is converted to 1 as there maybe some driving required
                if (dist_km is 0):
                    df.loc[idx, 'DrivingDist'] = 1
                else:
                    df.loc[idx, 'DrivingDist'] = dist_km
                                
                df.loc[idx, 'Update'] = updateIncr
         
                # Calculate the multiplier for this row
                df.loc[idx, 'Mult'] = df.loc[idx, 'DrivingDist']/df.loc[idx, 'LOSD']
            
                # Increment the lookup counter
                lookupsDone += 1
            else: 
                print("NOTE: Skipping Idx:", idx, " Ori:", df.loc[idx, 'Origin'], 
                      " Dest:", df.loc[idx, 'Destination'])

        if (i%100 is 0):
            print("Lookups:" + str(lookupsDone) + " Tries:" + str(i) + ". Time: " + 
                  str(datetime.datetime.now().strftime('%H:%M:%S')))
        i+=1

               
    cumMult_list = []
                        
    # Calculate Aggregates
    print("Iteration   Cumulative Avg")
    for i in range(1, updateIncr+1):
        cumMult = round(df['Mult'][(df['Update'] <= i) & 
                                   (df['Update'] != 0)].mean(),2)
        
        cumMult_list.append(cumMult)
        print(i, "         ", cumMult)
    
    updateCount = df['Mult'][df['Update'] != 0].count()
    print("Total Updates: ", updateCount)    
        
    # Write the data back to the same CSV     
    df.set_index('Origin', inplace=True)
    df.to_csv(directory + '/' + filename)
    print('Done with.... ' + filename)

    return (filename, cumMult_list, updateCount)


def main_program():
    
    directory = '4_CostLists'
    
    results = []

    for filename in os.listdir(directory):
        result = do_lookups(directory, filename)
        results.append(result)
    
    for result in results:
        print(result)
        
main_program()