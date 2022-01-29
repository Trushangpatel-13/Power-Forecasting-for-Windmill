import pandas as pd

url = "C:/Users/Lenovo/Desktop/Windmill Power Forecast/03 Building Models - TimeSeries/T1.csv"
df = pd.read_csv(url)
#df.drop(['LV ActivePower (kW)'],axis=1)
df.rename(columns={'Date/Time':'Date','Theoretical_Power_Curve (KWh)':'Energy','LV ActivePower (kW)':'ActivePower',"Wind Speed (m/s)":"Speed","Wind Direction (°)":"Direction"},
                inplace=True)

df.to_csv('./Test/Test2.csv')

print(df.describe())