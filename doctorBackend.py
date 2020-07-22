import numpy as np
import pandas as pd

def docMonthlyPatientVisits(df, year,doc_id):
    df = df.copy()
    df = df.loc[df['DOC_ID']==doc_id]
    df = df.loc[df.index.year == year]
    # converting dataframe to numpy array and converting 2D array to 1D and then converting to list
    df = df[['DOC_ID']].resample('M').count().values.flatten().tolist()
    return df

def docPatientGenderVisits(df,year,doc_id):
    df = df.copy()
    df = df.loc[df['DOC_ID']==doc_id]
    df = df.loc[df.index.year == year]
    df = df.groupby("gender").MR_NO.count()
    return df.to_dict()

def docPatientGenderAgeVisits(df,year,doc_id):
    df = df.copy()
    df = df.loc[df['DOC_ID']==doc_id]
    df = df.loc[df.index.year == year]
    # test = []
    gp_1 = df[df['age']<=5]
    # test.append(gp_1.groupby('gender').MR_NO.count())
    gp_2 = df[np.logical_and(df['age']>5, df['age']<=18)]
    # test.append(gp_2.groupby('gender').MR_NO.count())
    gp_3= df[np.logical_and(df['age']>18, df['age']<=34)]
    # test.append(gp_3.groupby('gender').MR_NO.count())
    gp_4= df[np.logical_and(df['age']>34, df['age']<=65)]
    # test.append(gp_4.groupby('gender').MR_NO.count())
    gp_5= df[df['age']>65]
    # test.append(gp_5.groupby('gender').MR_NO.count())

    
    my_dict = {
        "lessThan_Five" : gp_1.groupby('gender').MR_NO.count().to_dict(),
        "Between_Five_And_Eighteen":gp_2.groupby('gender').MR_NO.count().to_dict(),
        "Between_18_And_34" : gp_3.groupby('gender').MR_NO.count().to_dict(),
        "Between_34_And_65" : gp_4.groupby('gender').MR_NO.count().to_dict(),
        "Greater_than_65":gp_5.groupby('gender').MR_NO.count().to_dict()
    }
    for key in my_dict.keys():
        if not ('F' in my_dict[key]):
            my_dict[key]['F'] = 0
        if not ('M' in my_dict[key]):
            my_dict[key]['M'] = 0

    female = []
    male = []
    for key in my_dict.keys():
        female.append([my_dict[key]['F']][0])
        male.append([my_dict[key]['M']][0])

    my_dict = {
        'female' : female,
        'male' : male
    }

    return my_dict

###################################################################################
####################### Doctors Screen Bubble Chart ###############################
###################################################################################
       
def doc_AgevsService(id): # doctor's id
    df = pd.read_csv('data.csv', parse_dates=['SERVICE_DATE', 'DOB'], index_col='SERVICE_DATE')
    df = df[df['DOC_ID'] == id]
    df['Age'] = (pd.Timestamp('now') - df['DOB']).astype('<m8[Y]')
    df['Age_Group'] = (df['Age']/10).astype('int')
    ind = list(df.set_index(['Age_Group', 'unique_service_id']).sort_index().index)
    temp_i,temp_j=-1,0
    count=0
    result = []
    for i,j in ind:
        if(temp_i==-1):
            temp_i = i
            temp_j = j
        if(i!=temp_i or j!=temp_j):
            result.append([temp_i,temp_j,count])
            count=0
            temp_i = i
            temp_j = j
        count = count+1
    result.append([temp_i,temp_j,count])
    return pd.DataFrame(result, columns=['Age Group', 'Service', 'Count'])