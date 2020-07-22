import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
import statsmodels.api as sm
from datetime import date

def yearlyTransaction(df, year):
    df = df.copy()
    df['year'] = pd.DatetimeIndex(df.index).year
    df['month'] = pd.DatetimeIndex(df.index).month
    df = df[['AMOUNT']]
    df = df[['AMOUNT']].resample('M').sum()
    df = df.loc[year]
    df = df.values
    y = df.flatten()
    return y.tolist()

def departmentalExpenses(dept_df, dept_year):
    dept_df = dept_df.copy()
    dept_df = dept_df.loc[dept_year, ['AMOUNT','SPECIALITY_NAME']]
    dept_count = dept_df.groupby('SPECIALITY_NAME')['AMOUNT'].sum()
    

    dept_exp_dict = {
        "departments":dept_count.keys().tolist(),
        "expenses":dept_count.values.tolist()
    }
    
    return dept_exp_dict


def genderChart(gender_df, gender_year):
    gender_df = gender_df.copy()
    gender_df = gender_df.loc[gender_year]
    gender_count = gender_df['gender'].value_counts().tolist()
    tags = gender_df['gender'].unique().tolist()
    gender_dict  = {
        'genderTags': tags,
        'genderCounts': gender_count
    }
    return gender_dict


def calculate_age(dtob):
    today = date.today()
    mnths = (today.month, today.day) < (dtob.month, dtob.day)
    return today.year - dtob.year - mnths

def count_values_in_range(series, range_min_1, range_max_1, range_min_2, range_max_2, range_min_3, range_max_3):
    
    # "between" returns a boolean Series equivalent to left <= series <= right.
    a = int(series.between(left=range_min_1, right=range_max_1).sum())
    b = int(series.between(left=range_min_2, right=range_max_2).sum())
    c = int(series.between(left=range_min_3, right=range_max_3).sum())
#     print(type(a), type(b), type(c))
#     above data type is changed to int bcz after summation its datatype was numpy.int64 which isn't serializeable by
#     JSON Encoder
    return (a, b, c)

def ageChart(age_df, age_year):
    age_df = age_df.copy()
    range_min_1, range_max_1, range_min_2, range_max_2, range_min_3, range_max_3 = 1, 18, 19, 40, 41, 150
    
    age_df['age'] = age_df.DOB.map(calculate_age)
    age_df = age_df.loc[age_year]
    age_grp = age_df[['age']].apply( func=lambda row: count_values_in_range(row, range_min_1, range_max_1, range_min_2, range_max_2, range_min_3, range_max_3), axis = 0)
    age_dict = {
        # "1_to_18": age_grp.age[0],
        # "18_to_40": age_grp.age[1],
        # "40+": age_grp.age[2]
        'ageData' : age_grp.age
    }
    return age_dict


###################################################################################
##################### Hospital Amount Transaction Prediction ######################
###################################################################################


def get_data():
    df = pd.read_csv('data.csv', parse_dates=['SERVICE_DATE', 'DOB'], index_col='SERVICE_DATE')
    df = df.loc['2018']
    df = df[['AMOUNT']]
    df = df[['AMOUNT']].resample('M').sum()
    ##Duplicating Data
    future_dates = [df.index[-1] + DateOffset(months = x) for x in range(0,121) ]
    future_dates_df = pd.DataFrame(index = future_dates[1:],
                                   columns = df.columns)
    future_dates_df.iloc[:12] = df.values + 10000
    future_dates_df.iloc[12:24] = df.values +20000
    future_dates_df.iloc[24:36] = df.values +35000
    future_dates_df.iloc[36:48] = df.values +42000
    future_dates_df.iloc[48:60] = df.values +50000
    future_dates_df.iloc[60:72] = df.values +60000
    future_dates_df.iloc[72:84] = df.values +60000
    future_dates_df.iloc[84:96] = df.values +60000
    future_dates_df.iloc[96:108] = df.values +70000
    future_dates_df.iloc[108:120] = df.values +80000
    df = pd.concat([df,future_dates_df])
    return df

def predict(values):
    df = get_data()
    model = sm.tsa.statespace.SARIMAX(df['AMOUNT'],
                                  order = (0,1,1), 
                                  seasonal_order = (0,1,1,12))
    results = model.fit()
    future_dates = [df.index[-1] + DateOffset(months = x) for x in range(0,values+1) ]
    future_dates_df = pd.DataFrame(index = future_dates[1:],
                               columns = ['AMOUNT'])
    future_dates_df['AMOUNT'] = results.predict(start=len(df), end=(len(df)+values), dynamic=True)
    return future_dates_df
 