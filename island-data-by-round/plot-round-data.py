import pandas as pd
import plotly.express as px  

# VARIABLES TO CHANGE:
round = 4
product_to_plot = 'PICNIC_BASKET'
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
fig = px.line(df, x = 'timestamp', y = 'mid_price', color = 'product', title=f'price history for round {round}, days {available_days}')
fig.show(renderer="browser")


def compare_basket_to_components():
    df_basket = df.loc[df['product'] == 'PICNIC_BASKET']
    df_basket = pd.DataFrame({'timestamp': df_basket['timestamp'], 'basket_price': df_basket['mid_price']})
    df_dips = df.loc[df['product'] == 'DIP']
    df_dips = pd.DataFrame({'timestamp': df_dips['timestamp'], 'mid_price': 4*df_dips['mid_price']})
    df_baguettes = df.loc[df['product'] == 'BAGUETTE']
    df_baguettes = pd.DataFrame({'timestamp': df_baguettes['timestamp'], 'mid_price': 2*df_baguettes['mid_price']})
    df_ukuleles = df.loc[df['product'] == 'UKULELE']
    df_ukuleles = pd.DataFrame({'timestamp': df_ukuleles['timestamp'], 'mid_price': df_ukuleles['mid_price']})

    df_dips = pd.merge(df_dips, df_baguettes, on=['timestamp'], how='left').set_index(['timestamp']).sum(axis=1).reset_index()
    df_dips = pd.merge(df_dips, df_ukuleles, on=['timestamp'], how='left').set_index(['timestamp']).sum(axis=1).reset_index()
    df_combined = df_dips.rename(columns={0: 'combined_price'})
    df_combined = pd.merge(df_combined, df_basket, on='timestamp')

    print(df_dips.head(4))
    print(df_combined.head(4))

    fig = px.line(df_combined, x ='timestamp', y = ['combined_price', 'basket_price'],\
                title='price of picnic basket as a whole vs as individual components')
    fig.show(renderer='browser')
compare_basket_to_components()

# restrict dataframe to one product only and calculate n point rolling average
df = df.loc[df['product'] == product_to_plot]
df['price_roll_avr'] = df.rolling(n)['mid_price'].mean()

# plot price history with rolling average
fig = px.line(df, x = 'timestamp', y = ['mid_price','price_roll_avr'], title=f'mid_price history with {n}point moving avg for {product_to_plot}')
fig.show(renderer="browser")