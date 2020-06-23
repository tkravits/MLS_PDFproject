import pdfplumber
import glob
import pandas as pd
import numpy as np
import seaborn as sns

df = []

x=0
while True:
    for g in glob.glob(r"C:\Users\tkravits\PycharmProjects\DocFeeAnalysis\MLS_PDFs" + "/*.pdf"):
        with pdfplumber.open(g) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # insert commas to separate variables and then remove excess strings
                text = text.replace('\n', ' ')
                df.append(text)
                print(text)
                x=+1
    break

df = pd.DataFrame(df)

df['Concession Amt'] = df.apply(''.join, axis=1).str.extract('((?<=Concession Amt: ).*$)')#Use positive look ahead.Basically anything after Concession:
df['Concession Amt']=df['Concession Amt'].str.replace('$','')#Replace $ with a white space
df['Concession Amt'] = df['Concession Amt'].str.split(' ', n=1, expand=True)
#df = pd.DataFrame([sub.split("**") for sub in df])
df[['Date', 'Page']] = df[0].str.split('1 Per', n=1, expand=True)
df[['MLS #', 'Price']] = df[0].str.split('PRICE: ', n=1, expand=True)
df[['MLS Data', 'MLS #']] = df['MLS #'].str.split('MLS # : ', n=1, expand=True)
df[['Listing Price', 'Other']] = df['Price'].str.split(' ', n=1, expand=True)
df['Listing Price'] = df['Listing Price'].str.strip('$')
df['Listing Price'] = df['Listing Price'].str.replace(',', '')
df['Listing Price'] = df['Listing Price'].astype(float)

df['Concession Amt'] = df['Concession Amt'].str.replace(',', '')
df['Concession Amt'] = df['Concession Amt'].astype(float)

df[['Address', 'Other']] = df['Other'].str.split('Locale', n=1, expand=True)
df['Address'] = df['Address'].str.rstrip()
df[['Address', 'Status']] = df['Address'].str.rsplit(' ', n=1, expand=True)
df['Concession %'] = (df['Concession Amt'].divide(df['Listing Price'])) * 100

df = df[df['Status'].str.contains("SOLD")]

df = df[['MLS #', 'Date', 'Address', 'Status', 'Listing Price', 'Concession Amt', 'Concession %']]
df = df.drop_duplicates()
df = df.drop_duplicates(subset='Address', keep='last')

conditions = [(df['Concession %'] > 0) & (df['Status'] == 'SOLD'),
             (df['Concession Amt'] == np.NaN) & (df['Status'] == 'SOLD')]
choices = ['Concession', ' no concession']
df['Concession_check'] = np.select(conditions, choices, default='No Concession')
# df = df.sort_values(by='Listing Price', ascending=True)

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

range_choices = ['<100k', '100 - 200k', '200 - 300k', '300 - 400k', '400 - 500k', '500 - 600k', '600 - 700k',
                 '700 - 800k', '800 - 900k', '900 - 1m', '1m - 1.25m', '1.25m - 1.5m', '1.5m - 2m', '2m+']
df['Price Range'] = np.select(range_condit, range_choices, default=0)

df = df.sort_values(by='Listing Price', ascending=True)

g = sns.catplot(x="Price Range", y="Concession %", hue="Price Range", data=df,
                height=6, kind='swarm', palette="pastel")
g.despine(left=True)
g.set_ylabels("Concession %")