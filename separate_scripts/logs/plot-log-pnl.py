# program reads a log file and plots the cumulative PnL (profit and loss) with time 
# assuming the file is a .txt which starts after the 'Activities log:' (ie. no console outputs)

import pandas as pd
import plotly.express as px  

# ***change location of file here***
filename = 'log2.txt'
df =  pd.read_csv(f'separate_scripts\\logs\\{filename}', delimiter = ';') # Read csv file into dataframe

# plot price history
fig = px.line(df, x = 'timestamp', y = 'profit_and_loss', color = 'product', title = f'file: {filename}')
fig.show(renderer="browser")