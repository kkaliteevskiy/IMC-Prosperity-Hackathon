#%%

import pandas as pd
import plotly.express as px  


df =  pd.read_csv('day_1_data\\trades_round_1_day_0_nn.csv', delimiter = ';')# Read csv file into dataframe

#%%
#plot pricess

fig = px.line(df, x = 'timestamp', y = 'price', color = 'symbol')#create plot
fig.show(renderer="browser")


# %%
