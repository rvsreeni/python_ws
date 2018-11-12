#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 21:32:04 2018

@author: macuser
"""

### Web Scraping using Beautiful Soup

## Part A - Build a Dataframe 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

#from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "http://www.hubertiming.com/results/2017GPTR10K"
html = urlopen(url)

soup = BeautifulSoup(html, 'lxml')
type(soup)

rows = soup.find_all('tr')

# Remove HTML tags
list_rows = []
for row in rows:
    row_td = row.find_all('td')
    #print(row_td)
    #type(row_td)
    str_cells = str(row_td)
    cleantext = BeautifulSoup(str_cells, "lxml").get_text()
    #print(cleantext)
    list_rows.append(cleantext)

# Convert the list into a dataframe
df = pd.DataFrame(list_rows)
print(df.head(10))



## Part B - Data Manipulation and Cleaning

# Split the "0" column into multiple columns at the comma position
df1 = df[0].str.split(',', expand=True)

# Remove unwanted square brackets surrounding each row using the strip() method 
df1[0] = df1[0].str.strip('[')

# Get Table headers and convert into Pandas dataframe
col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)

df2 = pd.DataFrame(all_header)

# Split column "0" into multiple columns at the comma position for all rows.
df3 = df2[0].str.split(',', expand=True)

# two dataframes can be concatenated into one
frames = [df3, df1]
df4 = pd.concat(frames)

# assign the first row to be the table header
df5 = df4.rename(columns=df4.iloc[0])

# Overview of the data
df5.info()
print(df5.shape)

# drop all rows with any missing values.
df6 = df5.dropna(axis=0, how='any')

# remove table header
df7 = df6.drop(df6.index[0])

# rename columns
df7.rename(columns={'[Place': 'Place'},inplace=True)
df7.rename(columns={' Team]': 'Team'},inplace=True)

# remove the closing bracket
df7['Team'] = df7['Team'].str.strip(']')



## Part C - Data Analysis and Visualization

# 1) What was the average finish time (in minutes) for the runners?

time_list = df7[' Chip Time'].tolist()

# for loop to convert 'Chip Time' to minutes
time_mins = []
for i in time_list:
    h, m, s = i.split(':')
    math = (int(h) * 3600 + int(m) * 60 + int(s))/60
    time_mins.append(math)

df7['Runner_mins'] = time_mins

df7.describe(include=[np.number])

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])

# 2) Did the runners' finish times follow a normal distribution?
x = df7['Runner_mins']
ax = sns.distplot(x, hist=True, kde=True, rug=False, color='m', bins=25, hist_kws={'edgecolor':'black'})
plt.show()

# 3) Whether there were any performance differences between males and females of various age groups
f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']
sns.distplot(f_fuko, hist=True, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Female')
sns.distplot(m_fuko, hist=False, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Male')
plt.legend()

g_stats = df7.groupby(" Gender", as_index=True).describe()
print(g_stats)

df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel('Chip Time')
plt.suptitle("")


