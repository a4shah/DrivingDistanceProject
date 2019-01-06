#!/usr/bin/python3
# CRA OCAD Project
# 
# CostLOSD.py 
# Created for group project: 
# Andrew Campbell, Xiang Gao, Gurleen Kaur and Apurv Shah
# Algonquin College
# Date: Mar 24, 2018
# This file calculates the final cost for the Line of Sight Distance (LOSD) 
# and driving distance between all origin and destination combinations.
#
# Train Fares
# =========
# https://www.viarail.ca/sites/all/files/media/pdfs/About_VIA/our-company/annual-reports/2016/2016_Annual%20Report_EN.pdf
# 
# 2016 Via Rail Annual Report 
# Passenger Revenue $301.1M
# Ridership: 3,974,000
# Average fare: $75.77
# Round Trip Average Fare: $152
# 
# Airfare
# -------
# http://www.statcan.gc.ca/pub/51-004-x/51-004-x2017022-eng.htm
# Average Domestic Airfare for 2016 (one-way)
# 167.50
# 
# Average Train/Flight Costs:
# $75.77 + 167.50 / 2 = 121.64
#
# For NU/NWT/Yukon, sample at these 4 dates from www.expedia.ca
# 
# Flight               May 15  Aug 15  Nov 15   Feb 15   Average  One-way
# Toronto-Iqaluit NU   $1,801  $1,939  $1,801   $1,932   $1,868   $934
# Vancouver-Whitehorse $536    $609     $350    $609     $526     $263
# Edmonton-Inuvik      $954    $977     $954    $977     $966     $483


import pandas as pd
import os

def generate_costs(directory, filename):
    print('Working on.... ' + filename)

    # Read the source
    df = pd.read_csv(directory+'/'+filename, header=0)
     
    finalDist_list = []
    finalCost_list = []
      
    multiplier = df['Mult'][(df['Update'] != 0)].mean()
    print("Using Multiplier of ", round(multiplier,2))       
    
    # Iterate through the list of combinations of origins and destinations
    for series_index, row in df.iterrows():
        
        if (series_index%10000 is 0):
            print(series_index)
        
        # Load row into variables
        origin = df.Origin[series_index]
        dest   = df.Destination[series_index]
        losd   = df.LOSD[series_index]
        update = df.Update[series_index]
        drDist = df.DrivingDist[series_index]
 
        #print(origin, dest, losd)

        if (update == 0 and losd < 300): 
            updatedDist = losd * multiplier
        elif (update > 0 and losd < 300):
            updatedDist = drDist
        else:
            updatedDist = losd
            
        #print(" update", update, losd, multiplier, updatedDist)
        
        # If updatedDist is 0, it means the clinics are close by
        # However, there is some cost to drive from clinic to clinic 
        # Assume a cost based on distance of 5km. 
        if (updatedDist == 0):
            updatedDist = 5
        
        ontarioPCList = ['K', 'L', 'M', 'N', 'P']
        prairiePCList = ['R', 'S', 'T']
        
        if (origin[:1] == 'X' and dest[:1] in ontarioPCList):
            cost =  934
        elif (origin[:1] in ontarioPCList and dest[:1] == 'X'):
            cost =  934
        elif (origin[:1] == 'X' and dest[:1] in prairiePCList):
            cost =  483
        elif (origin[:1] in prairiePCList and dest[:1] == 'X'):
            cost =  483
        elif (origin[:1] == 'Y' and dest[:1] != 'Y'):
            cost =  263
        elif (origin[:1] != 'Y' and dest[:1] == 'Y'):
            cost =  263
        elif(updatedDist >= 300):
            cost = 121.64
        else:
            cost = (0.5 * updatedDist)        
            
        finalDist_list.append(updatedDist)
        finalCost_list.append(cost)
    
    df['Final_Dist']   = finalDist_list
    df['Final_Cost']   = finalCost_list
            
    # Calculate Aggregates
    avg = round(df['Final_Dist'].mean())
    total = round(df['Final_Dist'].sum())
    cnt = len(df)
    totalCost = round(df['Final_Cost'].sum())
    print(filename, avg, total, cnt, totalCost)


    updateIncr = df['Update'].max()
    print("Iteration   Cumulative Avg")
    for i in range(1, updateIncr+1):
        cumMult = round(df['Mult'][(df['Update'] <= i) & 
                                   (df['Update'] > 0)].mean(),2)
        print(i, "         ", cumMult)

    # Find the total cost for flying and total cost for driving        
    u300Cost = round(df['Final_Cost'][df['Final_Dist'] < 300].sum())
    o300Cost = round(df['Final_Cost'][df['Final_Dist'] >= 300].sum())

    # Get all the entries where lookups were done through Google 
    # This will allow us to calculate the correlation factor
    losd_list = df['LOSD'][df['Update'] > 0]
    final_list = df['Final_Dist'][df['Update'] > 0]
    result = pd.concat([losd_list, final_list], axis=1, join='inner')
    
    # Calculate the Pearson Correlation Coefficient 
    corr = round(result['LOSD'].corr(result['Final_Dist']),2)
    print("Correlation ", corr)

    # Write the data to a new CSV to allow comparision    
    df.set_index('Origin', inplace=True)
    df.to_csv('5_FinalLists/' + filename)
    print('Done with.... ' + filename)

    return (filename, avg, total, cnt, cumMult, totalCost, u300Cost, o300Cost, corr)

def main_program():
    directory = '4_CostLists'
    
    results = []

    for filename in os.listdir(directory):
        result = generate_costs(directory, filename)
        results.append(result)
    
    print("Region   AvgDist  TotalDist  TotalRec Mult TotalCost u300Cost o300Cost corr")
    for result in results:
        print(result)
        
main_program()