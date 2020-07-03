# Installing all requred libraries
import pandas as pd
import os

# Read the 1st month of csv
df = pd.read_csv('./SalesAnalysis/Sales_Data/Sales_April_2019.csv')

# Check the first 5 rows
df.head()

# When having multiple csv, use os.listdir()
files = [file for file in os.listdir('./SalesAnalysis/Sales_Data/')]

for file in files:
    print(file)
    
# output:
# Sales_December_2019.csv
# Sales_April_2019.csv
# Sales_February_2019.csv
# Sales_March_2019.csv
# Sales_August_2019.csv
# Sales_May_2019.csv
# Sales_November_2019.csv
# Sales_October_2019.csv
# Sales_January_2019.csv
# Sales_September_2019.csv
# Sales_July_2019.csv
# Sales_June_2019.csv


# Read all the csv files into one dataframe and export it into one big csv

files = [file for file in os.listdir('./SalesAnalysis/Sales_Data/')]

# Create an empty dataframe
all_months_data = pd.DataFrame()

for file in files:
    df = pd.read_csv('./SalesAnalysis/Sales_Data/' + file)
    all_months_data = pd.concat([all_months_data, df])

all_months_data.to_csv('all_data.csv', index = False)

# Read in the updated csv
all_data = pd.read_csv('all_data.csv')
all_data

# Sort through data according to date and reset index

all_data = all_data.sort_values(by=['Order Date']).reset_index()
all_data.head()

# Check where are the nan rows
nan_df = all_data[all_data.isna().any(axis = 1)]
nan_df.head()

# Drop all nan rows (we only have complete nan rows)
all_data = all_data.dropna(how = 'all')
all_data.head()

# Find 'or' and clean it up
# there seems to be a lot of duplicated rows and the first two words in 'Order Date' columns is 'Or'
# temp_data = all_data[all_data['Order Date'].str[0:2] == 'Or']
# temp_data

# so now we can simply do this
all_data = all_data[all_data['Order Date'].str[0:2] != 'Or']
all_data

# Create 'Month' column from 'Order Date' column, turn the content into string and take the first 2 words
all_data['Month'] = all_data['Order Date'].str[0:2]

# Change type of each value in 'Month' column to int
all_data['Month'] = all_data['Month'].astype('int32')
all_data

# Convert columns into correct type
all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered']) #Make int
all_data['Price Each'] =  pd.to_numeric(all_data['Price Each']) #Make float

# Here uses .to_numeric() which gives us either float64 or int64

# Add Sales column
all_data['Sales'] = all_data['Quantity Ordered'] * all_data['Price Each']
all_data

# Add a city column
# use lambda x to represent cell content
# .apply() : apply a function along an axis of the DataFrame. Default is the DataFrame’s index (axis=0).

# Create a column 'Column' from 'Purchase Address' column
# split city name from the string, which is between two commas 
# first time we can write as:
# all_data['Column'] = all_data['Purchase Address'].apply(lambda x: x.split(',')[1]) 

# We can then use a function to wrap it up
def get_city(address):
    return address.split(',')[1]

def get_state(address):
    return address.split(',')[2].split(' ')[1]

# different ways to format the cell content
# all_data['City'] = all_data['Purchase Address'].apply(lambda x: get_city(x) + ' (' +get_state(x) + ')') 
all_data['City'] = all_data['Purchase Address'].apply(lambda x: f"{get_city(x)} ({get_state(x)})") 

# As we had added a column, 'Column', so to drop it, we can do this:
# all_data = all_data.drop(columns = 'Column')
# or set inplace = True
# all_data.drop(columns = 'Column', inplace = True)

all_data

# Now come back to our Question 1: What was the best month for sales? How much was earned that month?

# .groupby() puts the same values as a group; then we sum them up
all_data.groupby(['Month']).sum()

# we can plot the above finding into a quick plot
import matplotlib.pyplot as plt

# x value of our bar chart
months = range(1, 13)

# y value of our bar chart, only including 'Sales' column
results = all_data.groupby(['Month']).sum()['Sales']

plt.bar(months, results)

# add labels
plt.xticks(months)
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month')

plt.show()

all_data.groupby(['City']).sum()

city_sales_df = all_data.groupby(['City']).sum()['Sales']
# type(city_sales_df) #output: series

# convert series to dataframe and plot to bar chart directly
city_sales_df.to_frame().plot.bar()

# reference: https://stackoverflow.com/questions/40313727/bar-graph-from-dataframe-groupby

# we can convert 'Order Date' into datatime format using pd.to_datetime()
all_data['Order Date'] = pd.to_datetime(all_data['Order Date'])
all_data

# now we can get hours, month, etc. easily from 'Order Date' column by using pandas.Series.dt.hour
all_data['Hour'] = all_data['Order Date'].dt.hour
all_data['Minute'] = all_data['Order Date'].dt.minute
all_data.head()

# plot it out
# show each hour's total sales
time_sales_df = all_data.groupby(['Hour']).sum()['Sales'].to_frame()
time_sales_df 

# y value here is sales made by each hour
plot = time_sales_df.plot.line(grid = True)
plot.set_xticks(range(len(time_sales_df))) #show all xticks by length of our dataframe

# find duplicated rows by 'Order ID'
# keep both duplicated and original 'Order ID' rows
order_product_df = all_data[all_data['Order ID'].duplicated(keep=False)]
order_product_df

# source: https://queirozf.com/entries/pandas-dataframe-examples-duplicated-data

# use transform to group items out of same Order ID into a new column called Grouped
# if used apply, Grouped will be filled with NaN

# df['Grouped'] = df.groupby(['Order ID'])['Product_code'].transform(lambda x: (',').join(x))
order_product_df['Grouped'] = order_product_df.groupby(['Order ID'])['Product'].transform(lambda x: (',').join(x))
order_product_df

# then we drop out the duplicated rows

order_product_df2 = order_product_df[['Order ID', 'Grouped']].drop_duplicates()
order_product_df2['Grouped_sort'] = order_product_df2['Grouped'].map(lambda x: ','.join(sorted(x.split(','))))
order_product_df2

from itertools import combinations
from collections import Counter

count = Counter()

for row in order_product_df2['Grouped_sort']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))

# for key, value in count.most_common(10):
#     print(key, value)
    
# count.most_common() is a list, so convert it to dataframe
product_pair_df = pd.DataFrame(count.most_common(10), columns = ['Product_pair', 'Counts'])
product_pair_df.plot.bar(x = 'Product_pair')

# plot product and quantity ordered
product_sales_df = all_data.groupby(['Product']).sum()['Quantity Ordered'].to_frame()
product_sales_df

product_sales_df.plot.bar()

# plot product and quantity ordered
price_each_df = all_data.groupby(['Product']).mean()['Price Each'].to_frame()
price_each_df

price_each_df.plot.line()

# overlay above charts
import matplotlib.pyplot as plt

ax = price_each_df.plot.line(figsize=(12,6), style='g-')
product_sales_df.plot.bar(figsize=(12,6), ax=ax, secondary_y=True)

plt.show()

# source: https://stackoverflow.com/questions/23482201/plot-pandas-dataframe-as-bar-and-line-on-the-same-one-chart
# source: https://stackoverflow.com/questions/11640243/pandas-plot-multiple-y-axes