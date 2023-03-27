import pandas as pd
import plotly.express as px  

# VARIABLES TO CHANGE:
round = 4
product_to_plot = 'DIVING_GEAR'
n = 10 # for an n-point rolling avg - see later
available_days = [round-3,round-2,round-1]




# Read csv file for each day into dataframe
df_1 =  pd.read_csv(f'island-data-by-round\\round-{round}-data\\prices_round_{round}_day_{available_days[0]}.csv', delimiter = ';')
df_2 =  pd.read_csv(f'island-data-by-round\\round-{round}-data\\prices_round_{round}_day_{available_days[1]}.csv', delimiter = ';')
df_3 =  pd.read_csv(f'island-data-by-round\\round-{round}-data\\prices_round_{round}_day_{available_days[2]}.csv', delimiter = ';')

# increment timestamps of all days so they line up in a row after each other
final_timestamp_day_minus1 = df_1['timestamp'].iloc[-1]
df_2['timestamp'] = df_2['timestamp'] + final_timestamp_day_minus1
final_timestamp_day_0 = df_2['timestamp'].iloc[-1]
df_3['timestamp'] = df_3['timestamp'] + final_timestamp_day_0

# join last 3 days of data together in one dataframe
df = pd.concat([df_1, df_2, df_3])

# plot price history
fig = px.line(df, x = 'timestamp', y = 'mid_price', color = 'product')
fig.show(renderer="browser")

# restrict dataframe to one product only and calculate n point rolling average
df = df.loc[df['product'] == product_to_plot]
df['price_roll_avr'] = df.rolling(n)['mid_price'].mean()

# plot price history with rolling average
fig = px.line(df, x = 'timestamp', y = ['mid_price','price_roll_avr'], title=f'mid_price history with {n}point moving avg for {product_to_plot}')
fig.show(renderer="browser")