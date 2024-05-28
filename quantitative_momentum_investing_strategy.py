# -*- coding: utf-8 -*-
"""Quantitative_Momentum_Investing_Strategy.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12XfBsKUqSoX6lGQ-TZ6IXtWFZQfCVXdz
"""

!pip install xlsxwriter

import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for
import math #The Python math module
from scipy import stats #The SciPy stats module

stocks = pd.read_csv('NIFTY_50_stocks.csv', skiprows=1)
print(stocks.head())

# Read the CSV file while skipping the first row
data = pd.read_csv('Nifty_50_Data.csv', skiprows=1)

# Add the 'Number of Shares to Buy' column with initial value 'N/A'
data['Number of Shares to Buy'] = 'N/A'

# Remove '\n' from column names
data.columns = data.columns.str.replace('\n', '')
data.head()

data.columns = data.columns.str.strip()
print(data.columns)

# Create DataFrame
df = pd.DataFrame(data)

# Convert columns to numeric
df['Price'] = pd.to_numeric(df['Price'].str.replace(',', ''))
df['30 D   %CHNG'] = pd.to_numeric(df['30 D   %CHNG'])
df['365 D % CHNG'] = pd.to_numeric(df['365 D % CHNG'])

# Calculate price returns
df['1-month price returns'] = df['Price'] * (1 + df['30 D   %CHNG'] / 100)
df['3-month price returns'] = df['Price'] * (1 + df['30 D   %CHNG'] / 100) ** 3
df['6-month price returns'] = df['Price'] * (1 + df['30 D   %CHNG'] / 100) ** 6
df['1-year price returns'] = df['Price'] * (1 + df['365 D % CHNG'] / 100)

df.head()

# Calculate momentum percentiles
time_periods = ['1-month', '3-month', '6-month', '1-year']
for row in df.index:
    for time_period in time_periods:
        percentile = stats.percentileofscore(df[f'{time_period} price returns'], df.loc[row, f'{time_period} price returns']) / 100
        df.loc[row, f'{time_period} Return Percentile'] = percentile

from statistics import mean
# Calculate HQM Score
for row in df.index:
    momentum_percentiles = [df.loc[row, f'{time_period} Return Percentile'] for time_period in time_periods]
    df.loc[row, 'HQM Score'] = mean(momentum_percentiles)

# Select top 50 stocks based on HQM Score
hqm_dataframe = df.sort_values(by='HQM Score', ascending=False).head(5).reset_index(drop=True)

hqm_dataframe.head()

# Calculate number of shares to buy
portfolio_size = float(input("Enter the value of your portfolio: "))

position_size = portfolio_size / len(hqm_dataframe.index)
hqm_dataframe['Number of Shares to Buy'] = (position_size / hqm_dataframe['Price']).apply(math.floor)

hqm_dataframe

hqm_dataframe.columns

# Define the file name
file_name = "momentum_strategy.xlsx"

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

# Write the DataFrame to the Excel file
hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index=False)

# Get the xlsxwriter workbook and worksheet objects
workbook  = writer.book
worksheet = writer.sheets['Momentum Strategy']

## Define formats for the columns
background_color = '#0a0a23'
font_color = '#ffffff'

string_template = workbook.add_format({'font_color': font_color, 'bg_color': background_color, 'border': 1})
rupee_template = workbook.add_format({'num_format': '\u20B9#,##0.00', 'font_color': font_color, 'bg_color': background_color, 'border': 1})
integer_template = workbook.add_format({'num_format': '0', 'font_color': font_color, 'bg_color': background_color, 'border': 1})
percent_template = workbook.add_format({'num_format': '0.0%', 'font_color': font_color, 'bg_color': background_color, 'border': 1})

workbook  = writer.book
# Define column formats
column_formats = {
    'A': ['SYMBOL', string_template],
    'B': ['Price', rupee_template],
    'C': ['VOLUME (shares)', integer_template],
    'D': ['52W H', rupee_template],
    'E': ['52W L', rupee_template],
    'F': ['30 D   %CHNG', percent_template],
    'G': ['365 D % CHNG', percent_template],
    'H': ['Number of Shares to Buy', integer_template],
    'I': ['1-month price returns', percent_template],
    'J': ['3-month price returns', percent_template],
}

# Set column formats
for column, (header, format_) in column_formats.items():
    worksheet.set_column(f'{column}:{column}', 20, format_)
    worksheet.write(f'{column}1', header, string_template)

# Save the Excel file
workbook.close()
from google.colab import files

files.download('momentum_strategy.xlsx')