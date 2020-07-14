# This is designed to pull meaningful information from MLS pdfs and put them into a dataframe for analysis

import pdfplumber
import glob
import pandas as pd
import numpy as np
import seaborn as sns

# establish an empty dataframe for pdfplumber to fill
df = []

# looks in the folder for any PDFs, pdfplumber will extract the text per the page and loop through all the PDFs
# until there are no more pages left
x=0
while True:
    for g in glob.glob(r"C:\Users\tkravits\PycharmProjects\DocFeeAnalysis\MLS_PDFs" + "/*.pdf"):
        with pdfplumber.open(g) as pdf:
            for page in pdf.pages:
                # extracts the text
                text = page.extract_text()
                # replaces new lines with an empty space
                text = text.replace('\n', ' ')
                # adds to a list
                df.append(text)
                print(text)
                x=+1
    break

# converts the list into a dataframe
df = pd.DataFrame(df)

# Use negative look behind basically anything after "Concession Amt:" will be pulled
#df['Concession Amt'] = df.apply(''.join, axis=1).str.extract('((?<=Concession Amt: ).*$)')
df['Concession Amt'] = df.apply(''.join, axis=1).str.extract('((?<=Sold Price: ).*$)')

# Replace $ with a white space
df['Concession Amt']=df['Concession Amt'].str.replace('$','')
# Splits the Concession Amount will all the other information to create a stand alone number
df['Concession Amt'] = df['Concession Amt'].str.split(' ', n=1, expand=True)

# Splits the columns into Date, Page, MLS #, Price using established rules, n=1 takes the first instance
df[['Date', 'Page']] = df[0].str.split('1 Per', n=1, expand=True)
df[['MLS #', 'Price']] = df[0].str.split('PRICE: ', n=1, expand=True)
df[['MLS Data', 'MLS #']] = df['MLS #'].str.split('MLS # : ', n=1, expand=True)
df[['Listing Price', 'Other']] = df['Price'].str.split(' ', n=1, expand=True)

# Removes $ , and converts it to a float. Float needs to be used because later on, some of the concession amounts are
# NaN, and if Listing Price is a float, it can skip NaNs
df['Listing Price'] = df['Listing Price'].str.strip('$')
df['Listing Price'] = df['Listing Price'].str.replace(',', '')
df['Listing Price'] = df['Listing Price'].astype(float)

# Converts string to a float for calculation
df['Concession Amt'] = df['Concession Amt'].str.replace(',', '')
df['Concession Amt'] = df['Concession Amt'].astype(float)

# Splits on Locale and removes the white space
df[['Address', 'Other']] = df['Other'].str.split('Locale', n=1, expand=True)
df['Address'] = df['Address'].str.rstrip()

# Splits the Address so that the code can figure out if a property is sold
df[['Address', 'Status']] = df['Address'].str.rsplit(' ', n=1, expand=True)
df[['Address', 'Type']] = df['Address'].str.split('(?<=\d{5})\s+', expand=True)

# Calculates the percentage conceeded by a property based on the Listing Price
df['Concession %'] = ((df['Listing Price'] - (df['Concession Amt'])).divide(df['Listing Price']) * 100)

# removes properties that aren't sold
df = df[df['Status'].str.contains("SOLD")]

# cleans up the dataframe, only pulling the needed info
df = df[['MLS #', 'Date', 'Address', 'Status', 'Listing Price', 'Concession Amt', 'Concession %']]

# Drops any duplicates, sometimes the same property is in multiple MLS listings
df = df.drop_duplicates()
df = df.drop_duplicates(subset='Address', keep='last')

# sets the conditions so that if a Concession percentage is greater than 0 and is sold, put it in as a Concession (True)
# if there is no concession and it's sold, set to No Concession (False)
conditions = [(df['Concession %'] > 0) & (df['Status'] == 'SOLD'),
             (df['Concession Amt'] == np.NaN) & (df['Status'] == 'SOLD')]
choices = ['Concession', 'no concession']

# creates a column based on whether there was a concession or not
df['Concession_check'] = np.select(conditions, choices, default='No Concession')

# sets the condition based on a 100K range in listing prices. This is done to prepare the data to graph
range_condit = [(df['Listing Price'] <= 100000), (df['Listing Price'] > 100000) & (df['Listing Price'] <= 200000),
                ((df['Listing Price'] > 200000) & (df['Listing Price'] <= 300000)),
                ((df['Listing Price'] > 300000) & (df['Listing Price'] <= 400000)),
                ((df['Listing Price'] > 400000) & (df['Listing Price'] <= 500000)),
                ((df['Listing Price'] > 500000) & (df['Listing Price'] <= 600000)),
                ((df['Listing Price'] > 600000) & (df['Listing Price'] <= 700000)),
                ((df['Listing Price'] > 700000) & (df['Listing Price'] <= 800000)),
                ((df['Listing Price'] > 800000) & (df['Listing Price'] <= 900000)),
                ((df['Listing Price'] > 900000) & (df['Listing Price'] <= 1000000)),
                ((df['Listing Price'] > 1000000) & (df['Listing Price'] <= 1250000)),
                ((df['Listing Price'] > 1250000) & (df['Listing Price'] <= 1500000)),
                ((df['Listing Price'] > 1500000) & (df['Listing Price'] <= 2000000)),
                (df['Listing Price'] > 2000000)
                ]

# this will be the text that shows up in the column if it meets the conditions specified above
range_choices = ['<100k', '100 - 200k', '200 - 300k', '300 - 400k', '400 - 500k', '500 - 600k', '600 - 700k',
                 '700 - 800k', '800 - 900k', '900 - 1m', '1m - 1.25m', '1.25m - 1.5m', '1.5m - 2m', '2m+']

# creates a column based on the range in prices
df['Price Range'] = np.select(range_condit, range_choices, default=0)

# sorting the column from lowest to highest price
df = df.sort_values(by='Listing Price', ascending=True)

# using seaborn to graph the data, the x axis is the Price Range, the y axis is the Concession Percentage, and
# the type of graph is a category plot.
g = sns.catplot(x="Price Range", y="Concession %", hue="Price Range", data=df,
                height=6, kind='swarm', palette="muted")
g.despine(left=True)

# sets the title
g.fig.suptitle('Seller Concession Based on Listing Price')

# I then set the y label to have the title "Concession Percentage"
g.set_ylabels("Concession Percentage")