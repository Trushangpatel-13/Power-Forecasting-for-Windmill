import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


#function for finding months
def find_month(x):
    if " 01 " in x:
        return "Jan"
    elif " 02 " in x:
        return "Feb"
    elif " 03 " in x:
        return "March"
    elif " 04 " in x:
        return "April"
    elif " 05 " in x:
        return "May"
    elif " 06 " in x:
        return "June"
    elif " 07 " in x:
        return "July"
    elif " 08 " in x:
        return "August"
    elif " 09 " in x:
        return "Sep"
    elif " 10 " in x:
        return "Oct"
    elif " 11 " in x:
        return "Nov"
    else:
        return "Dec"


# function for rewriting wind speed for 0.5 intervals.
# For example: wind speeds between 3.25 and 3.75 turns 3.5,wind speeds between 3.75 and 4.25 turns 4.0
def mean_speed(x):
    list = []
    i = 0.25
    while i <= 25.5:
        list.append(i)
        i += 0.5

    for i in list:
        if x < i:
            x = i - 0.25
            return x


# function for rewriting wind direction for 30 intervals.
# For example: wind directions between 15 and 45 turns 30,wind speeds between 45 and 75 turns 60
def mean_direction(x):
    list = []
    i = 15
    while i <= 375:
        list.append(i)
        i += 30

    for i in list:
        if x < i:
            x = i - 15
            if x == 360:
                return 0
            else:
                return x

def find_direction(x):
    if x==0:
        return "N"
    if x==30:
        return "NNE"
    if x==60:
        return "NEE"
    if x==90:
        return "E"
    if x==120:
        return "SEE"
    if x==150:
        return "SSE"
    if x==180:
        return "S"
    if x==210:
        return "SSW"
    if x==240:
        return "SWW"
    if x==270:
        return "W"
    if x==300:
        return "NWW"
    if x==330:
        return "NNW"


def wind_speed_count(df):
    turbine_no="T1" #for powercurve graph
    data1_T=df.copy()
    data1_T.rename(columns={'LV ActivePower (kW)': 'ActivePower(kW)', "Wind Speed (m/s)": "WindSpeed(m/s)",
                            "Wind Direction (°)": "Wind_Direction"},
                   inplace=True)
    data1_T.rename(columns={'Date/Time': 'Time'}, inplace=True)
    data1_T['Month'] = data1_T.Time.apply(find_month)

    # adding a new column as "mean_WindSpeed" with function mean_speed().
    data1_T["mean_WindSpeed"] = data1_T["WindSpeed(m/s)"].apply(mean_speed)
    # adding a new column as "mean_Direction" with function mean_direction().
    data1_T["mean_Direction"] = data1_T["Wind_Direction"].apply(mean_direction)
    # adding a new column as "Direction" with function find_direction().
    data1_T["Direction"] = data1_T["mean_Direction"].apply(find_direction)

    data1_T["WindSpeed(m/s)"][data1_T["WindSpeed(m/s)"] > 25].value_counts()
    # Remove the data that wind speed is smaller than 3.5 and bigger than 25.5
    # We do that because according to turbine power curve turbine works between these values.
    data2_T = data1_T[(data1_T["WindSpeed(m/s)"] > 3.5) & (data1_T["WindSpeed(m/s)"] <= 25.5)]
    # Number of values where wind speed is bigger than 3.5 and active power is zero.
    # If wind speed is bigger than 3.5 and active power is zero, this means turbine is out of order. we must eliminate these.
    len(data2_T["ActivePower(kW)"][(data2_T["ActivePower(kW)"] == 0) & (data2_T["WindSpeed(m/s)"] > 3.5)])

    # Eliminate datas where wind speed is bigger than 3.5 and active power is zero.
    data3_T = data2_T[
        ((data2_T["ActivePower(kW)"] != 0) & (data2_T["WindSpeed(m/s)"] > 3.5)) | (data2_T["WindSpeed(m/s)"] <= 3.5)]
    # Number of values
    print(len(data3_T["WindSpeed(m/s)"]))

    # the mean value of Nordex_Powercurve(kW) when mean_WindSpeed is 5.5
    data3_T["Theoretical_Power_Curve (KWh)"][data3_T["mean_WindSpeed"] == 5.5].mean()

    # we create clean data and add a columns where calculating losses.
    # Loss is difference between the Nordex_Powercurve and ActivePower.
    data_T_clean = data3_T.sort_values("Time")
    data_T_clean["Loss_Value(kW)"] = data_T_clean["Theoretical_Power_Curve (KWh)"] - data_T_clean["ActivePower(kW)"]
    data_T_clean["Loss(%)"] = data_T_clean["Loss_Value(kW)"] / data_T_clean["Theoretical_Power_Curve (KWh)"] * 100
    # round the values to 2 digit.
    data_T_clean = data_T_clean.round({'ActivePower(kW)': 2, 'WindSpeed(m/s)': 2, 'Theoretical_Power_Curve (KWh)': 3,
                                       'Wind_Direction': 2, 'Loss_Value(kW)': 2, 'Loss(%)': 2})

    # creating summary speed dataframe from clean data.
    DepGroupT_speed = data_T_clean.groupby("mean_WindSpeed")
    data_T_speed = DepGroupT_speed.mean()
    # removing the unnecessary columns.
    data_T_speed.drop(columns={"WindSpeed(m/s)", "Wind_Direction", "mean_Direction"}, inplace=True)
    # creating a windspeed column from index values.
    listTspeed_WS = data_T_speed.index.copy()
    data_T_speed["WindSpeed(m/s)"] = listTspeed_WS
    # changing the place of columns.
    data_T_speed = data_T_speed[
        ["WindSpeed(m/s)", "ActivePower(kW)", "Theoretical_Power_Curve (KWh)", "Loss_Value(kW)", "Loss(%)"]]
    # changing the index numbers.
    data_T_speed["Index"] = list(range(1, len(data_T_speed.index) + 1))
    data_T_speed.set_index("Index", inplace=True)
    # rounding the values to 2 digit
    data_T_speed = data_T_speed.round(
        {"WindSpeed(m/s)": 1, 'ActivePower(kW)': 2, 'Theoretical_Power_Curve (KWh)': 3, 'Loss_Value(kW)': 2,
         'Loss(%)': 2})
    # creating a count column that shows the number of wind speed from clean data.
    data_T_speed["count"] = [len(data_T_clean["mean_WindSpeed"][data_T_clean["mean_WindSpeed"] == i])
                             for i in data_T_speed["WindSpeed(m/s)"]]
    data_T_speed.rename(columns={'Theoretical_Power_Curve (KWh)': 'Energy', 'ActivePower(kW)': 'Power',
                         "WindSpeed(m/s)": "Speed", "Loss_Value(kW)": "Loss_value", "count":"Count", "Loss(%)":"Loss"},
                inplace=True)
    #print(data_T_speed)
    return data_T_speed

def wind_direction_count(df):
    df.drop('LV ActivePower (kW)', axis=1)
    data1_T = df.copy()
    data1_T.rename(columns={'LV ActivePower (kW)': 'ActivePower(kW)', "Wind Speed (m/s)": "WindSpeed(m/s)",
                            "Wind Direction (°)": "Wind_Direction"},
                   inplace=True)
    data1_T.rename(columns={'Date/Time': 'Time'}, inplace=True)
    # add months
    data1_T['Month'] = data1_T.Time.apply(find_month)
    data1_T["mean_WindSpeed"] = data1_T["WindSpeed(m/s)"].apply(mean_speed)
    # adding a new column as "mean_Direction" with function mean_direction().
    data1_T["mean_Direction"] = data1_T["Wind_Direction"].apply(mean_direction)
    # adding a new column as "Direction" with function find_direction().
    data1_T["Direction"] = data1_T["mean_Direction"].apply(find_direction)
    # Values bigger than 25.
    data1_T["WindSpeed(m/s)"][data1_T["WindSpeed(m/s)"] > 25].value_counts()
    # Remove the data that wind speed is smaller than 3.5 and bigger than 25.5
    # We do that because according to turbine power curve turbine works between these values.
    data2_T = data1_T[(data1_T["WindSpeed(m/s)"] > 3.5) & (data1_T["WindSpeed(m/s)"] <= 25.5)]
    # Eliminate datas where wind speed is bigger than 3.5 and active power is zero.
    data3_T = data2_T[((data2_T["ActivePower(kW)"] != 0) & (data2_T["WindSpeed(m/s)"] > 3.5)) | (data2_T["WindSpeed(m/s)"] <= 3.5)]
    # the mean value of Nordex_Powercurve(kW) when mean_WindSpeed is 5.5
    data3_T["Theoretical_Power_Curve (KWh)"][data3_T["mean_WindSpeed"] == 5.5].mean()

    # we create clean data and add a columns where calculating losses.
    # Loss is difference between the Nordex_Powercurve and ActivePower.
    data_T_clean = data3_T.sort_values("Time")
    data_T_clean["Loss_Value(kW)"] = data_T_clean["Theoretical_Power_Curve (KWh)"] - data_T_clean["ActivePower(kW)"]
    data_T_clean["Loss(%)"] = data_T_clean["Loss_Value(kW)"] / data_T_clean["Theoretical_Power_Curve (KWh)"] * 100
    # round the values to 2 digit.
    data_T_clean = data_T_clean.round({'ActivePower(kW)': 2, 'WindSpeed(m/s)': 2, 'Theoretical_Power_Curve (KWh)': 2,
                                       'Wind_Direction': 2, 'Loss_Value(kW)': 2, 'Loss(%)': 2})
    # create summary direction dataframe from clean data.
    DepGroupT_direction = data_T_clean.groupby("Direction")
    data_T_direction = DepGroupT_direction.mean()
    # remove the unnecessary columns.
    data_T_direction.drop(columns={"WindSpeed(m/s)", "Wind_Direction"}, inplace=True)
    # create a column from index.
    listTdirection_Dir = data_T_direction.index.copy()
    data_T_direction["Direction"] = listTdirection_Dir
    # change the name of mean_WindSpeed column as  WindSpeed.
    data_T_direction["WindSpeed(m/s)"] = data_T_direction["mean_WindSpeed"]
    data_T_direction.drop(columns={"mean_WindSpeed"}, inplace=True)
    # change the place of columns.
    data_T_direction = data_T_direction[
        ["Direction", "mean_Direction", "ActivePower(kW)", "Theoretical_Power_Curve (KWh)", "WindSpeed(m/s)",
         "Loss_Value(kW)", "Loss(%)"]]
    # change the index numbers.
    data_T_direction["Index"] = list(range(1, len(data_T_direction.index) + 1))
    data_T_direction.set_index("Index", inplace=True)
    # create a count column that shows the number of directions from clean data.
    data_T_direction["count"] = [len(data_T_clean["Direction"][data_T_clean["Direction"] == i])
                                 for i in data_T_direction["Direction"]]
    # round the values to 2 digit
    data_T_direction = data_T_direction.round(
        {'WindSpeed(m/s)': 1, 'ActivePower(kW)': 2, 'Theoretical_Power_Curve (KWh)': 2,
         'Loss_Value(kW)': 2, 'Loss(%)': 2})
    # sort by mean_Direction
    data_T_direction = data_T_direction.sort_values("mean_Direction")
    data_T_direction.drop(columns={"mean_Direction"}, inplace=True)

    data_T_direction.rename(columns={'Theoretical_Power_Curve (KWh)': 'Energy', 'ActivePower(kW)': 'Power',
                                 "WindSpeed(m/s)": "Speed", "Loss_Value(kW)": "Loss_value", "count": "Count",
                                 "Loss(%)": "Loss"},
                        inplace=True)
    return data_T_direction


#url = "C:/Users/Lenovo/Desktop/Windmill Power Forecast/03 Building Models - TimeSeries/T1.csv"
#df = pd.read_csv(url)
#wind_speed_count(df)