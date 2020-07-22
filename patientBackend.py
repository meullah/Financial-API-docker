import pandas as pd

def patient_DocvsService(id):
    df = pd.read_csv('data.csv', parse_dates=['SERVICE_DATE', 'DOB'], index_col='SERVICE_DATE')
    df = df[df['MR_NO'] == id]
    ind = list(df.set_index(['DOC_ID', 'unique_service_id']).sort_index().index)
    temp_i,temp_j=-1,0
    count=0
    result = []
    ind
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
    return pd.DataFrame(result, columns=['DOC_ID', 'Service_ID', 'Count'])