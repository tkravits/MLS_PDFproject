import pandas as pd
import glob
import numpy as np

# imports the permit sheet to be cleaned up
for filename in glob.glob(r'C:\Users\tkravits\Github\MLS_PDFproject\MLS_Analysis_08032020.xlsx'):
    df_MLS = pd.read_excel(filename)

# imports the permit sheet to be cleaned up
for filename in glob.glob(r'C:\Users\tkravits\PycharmProjects\DocFeeAnalysis\Affordable_Housing_List.csv'):
    df_affr = pd.read_csv(filename)

df_MLS['Address'] = df_MLS['Address'].str.split('(?<=\d{5})\s+', expand=True)
df_MLS['Address'].replace(regex=True, inplace=True, to_replace=r',', value=r'')
df_MLS[['str_num', 'str_dir', 'str', 'str_sfx', 'unit', 'city', 'zip', 'col']] = df_MLS['Address'].str.split(expand=True)

df = df_MLS
mylist = ['N','E','W','S']
cities = ['Boulder', 'Lafayette', 'Longmont', 'Erie', 'Louisville', 'Lyons', 'Allenspark', 'Niwot', 'Superior']

m = ~df['str_dir'].isin(mylist)
c = ~df['unit'].isin(cities)
df.loc[m, 'str_dir':] = df.loc[m, 'str_dir':].shift(axis=1)
df.loc[c, 'unit':] = df.loc[c, 'unit':].shift(axis=1)
