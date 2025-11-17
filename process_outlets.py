import pandas as pd
import os

'''
Assumes locations folder containing per-person csv files
is in cwd along with the outlets csv (2018 Food Outlets and PA.csv)
 - Converted from initial .XLSM by opening it in excel and saving as csv
'''

def preprocess():
    # convert lat/long to digit form for later
    def int_to_digits(integer, place):
        string = str(integer)
        string = string[:place] + '.' + string[place:]
        return float(string)
    df = pd.read_csv('2018 Food Outlets and PA.csv')
    # filter out unrelated rows
    DESC = 'PRIMARY NAICS DESCRIPTION'
    good_desc = {'Full-Service Restaurants',
    'Limited-Service Restaurants',
    'Supermarkets/Other Grocery (Exc Convenience) Strs',
    'Convenience Stores',
    'Department Stores',
    'Warehouse Clubs & Supercenters',
    'Fruit & Vegetable Markets' }
    # brings row count from 21228 -> 13249 
    df = df[df[DESC].isin(good_desc)]
    # filter out unrelated columns
    good_cols = ['COMPANY NAME', 'CITY', 'LATITUDE', 'LONGITUDE', DESC]
    df = df[good_cols]
    # turn lat and long into decimal format
    df['LATITUDE'] = df['LATITUDE'].apply(int_to_digits, place=2)
    df['LONGITUDE'] = -df['LONGITUDE'].apply(int_to_digits, place=3)
    # could preprocess locations on the fly or do it here;
    # save new df in outlets.csv
    PATH = 'outlets.csv'
    # first remove to clear previous outlets.csv
    if os.path.exists(PATH):
        os.remove(PATH)
    df.to_csv(PATH, index=False)

preprocess()
