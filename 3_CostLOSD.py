#!/usr/bin/python3
# CRA OCAD Project
# 
# CostLOSD.py 
# Created for group project: 
# Andrew Campbell, Xiang Gao, Gurleen Kaur and Apurv Shah
# Algonquin College
# Date: Mar 24, 2018
# This file calculates the cost for the Line of Sight Distance (LOSD) between
# all origin and destination combinations.
#
# Cost Rules are as follows:   
# Flight Costs Rules
# Ontario-Nunavut (X) - $2000
# # BC-Yukon (Y) - $1000
# # Prairie-NWT (X) - $2000
# 300-499 km - $400
# >500 km - $600
# 
# Driving Distance Rules (LOSD)
# 0 -> 1km
# 50 cents per km


import pandas as pd
import os

def generate_costs(directory, filename):
    print('Working on.... ' + filename)

    # Read the source
    df = pd.read_csv(directory+'/'+filename, header=0)
     
    cost_list   = []
    dd_list     = []
    update_list = []
    mult_list   = []
    
    # Iterate through the list of combinations of origins and destinations
    for series_index, row in df.iterrows():
        
        if (series_index%10000 is 0):
            print(series_index)
        
        # Load row into variables
        origin = df.Origin[series_index]
        dest   = df.Destination[series_index]
        losd   = df.LOSD[series_index]
        
        # If losd is 0, it means the clinics are close by
        # However, there is some cost to drive from clinic to clinic 
        # Assume a cost based on distance of 5km. 
        if (losd == 0):
            losd = 5
        
        if (origin[:1] == 'X' and dest[:1] != 'X'):
            cost = 2000
        elif (origin[:1] != 'X' and dest[:1] == 'X'):
            cost = 2000
        elif (origin[:1] == 'Y' and dest[:1] != 'Y'):
            cost = 1000
        elif (origin[:1] != 'Y' and dest[:1] == 'Y'):
            cost = 1000
        elif(losd >= 500):
            cost = 600
        elif(losd >= 300):
            cost = 400
        else:
            cost = (0.5 * losd)        
            
        cost_list.append(cost)
        dd_list.append(0)
        update_list.append(0)
        mult_list.append(1)
    
    df['LOSD_Cost']   = cost_list
    df['DrivingDist'] = dd_list
    df['Update']      = update_list
    df['Mult']        = mult_list
            
    # Calculate Aggregates
    avg = round(df['LOSD'].mean())
    total = df['LOSD'].sum()
    cnt = len(df)
    totalCost = round(df['LOSD_Cost'].sum())
    print(filename, avg, total, cnt, totalCost)

    # Write the data to a new CSV to allow comparision    
    df.set_index('Origin', inplace=True)
    df.to_csv('4_CostLists/' + filename)
    print('Done with.... ' + filename)

    return (filename, avg, total, cnt, totalCost)

def main_program():
    directory = '3_ComboLists'
    
    results = []

    for filename in os.listdir(directory):
        result = generate_costs(directory, filename)
        results.append(result)
    
    for result in results:
        print(result)
        
main_program()