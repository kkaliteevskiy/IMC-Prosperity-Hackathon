#%%

#program reads log files and store them as a dataframe

import pandas as pd

#change location of file here
df_log =  pd.read_csv('C:\\Users\\kiril\\IMC Prosperity Hackathon\\logs\\log1.txt', delimiter = ';')# Read csv file into dataframe
