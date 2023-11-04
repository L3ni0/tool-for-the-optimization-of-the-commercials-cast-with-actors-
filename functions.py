import pandas as pd
import os
from datetime import date, timedelta

def read_all_data() -> pd.DataFrame:
    '''reading and concatinating all .csv files in data folder

        Return:
        df_main: DataFrame with all data in 'data' folder
    '''
    csv_files = ['data/'+file for file in os.listdir('data') if file.endswith('.csv')]
    df_main = pd.read_csv(csv_files[0])
    for file in csv_files[1:]:
        df_temp = pd.read_csv(file)
        df_main = pd.concat([df_main,df_temp])
    
    # df_main = df_main.dropna()


    return df_main.reset_index()


def split_filter_part(filter_part):
    operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

def create_summaries(df) -> pd.DataFrame:

    df_pivoted = df.pivot_table(index='star',columns='date',values='views').reset_index()
    newest = df_pivoted.columns[-1]

    df_pivoted = df_pivoted.dropna(subset=newest)

    newest_date = date.fromisoformat(newest)
    diff_7d = (newest_date - timedelta(days=7)).isoformat()
    diff_14d = (newest_date - timedelta(days=14)).isoformat()


    # creating cols and filling nans
    if diff_7d not in df_pivoted.columns:
        df_pivoted[diff_7d] = pd.NA

    to_chechk_date = date.fromisoformat(diff_7d)
    for _ in range(30):  

        to_chechk_date = to_chechk_date - timedelta(days=1)
        if not df_pivoted[diff_7d].isna().values.any():
                break
        
        if to_chechk_date.isoformat() in df_pivoted.columns:
            df_pivoted[diff_7d].fillna(df_pivoted[to_chechk_date.isoformat()], inplace=True)
            


    if diff_14d not in df_pivoted.columns:
        df_pivoted[diff_14d] = pd.NA

    to_chechk_date = date.fromisoformat(diff_14d)
    for _ in range(40):

        to_chechk_date = to_chechk_date - timedelta(days=1)
        if not df_pivoted[diff_14d].isna().values.any():
                break
        
        if to_chechk_date.isoformat() in df_pivoted.columns:
            df_pivoted[diff_14d].fillna(df_pivoted[to_chechk_date.isoformat()], inplace=True)
            
    
    # creating measurments
    df_pivoted['7d_%'] = 100 * (df_pivoted[newest] - df_pivoted[diff_7d]) / df_pivoted[diff_7d]
    df_pivoted['14d_%'] = 100 * (df_pivoted[newest] - df_pivoted[diff_14d]) / df_pivoted[diff_14d]
    df_pivoted['Current_Viewership'] = df_pivoted[newest]
    df_pivoted.drop(columns=df_pivoted.columns[1:-3], inplace=True)
    
    # adding general information
    df_info = pd.read_csv('data/information/general_information.csv',na_values=['None'],header=0)
    df_pivoted = df_pivoted.merge(df_info,on='star',how='inner')
    
    dtypes = {'star':'str',
              '7d_%':'float64',
              '14d_%': 'float64',
              'Current_Viewership':'Int64',
              'Age':'Int64',
              'Birthplace':'string',
              'Height':'Int64',
              'Weight':'Int64',
              'Gender':'string',
              'Ethnicity':'string',
              'Cost($)':'float64'     
    }


    return df_pivoted.astype(dtypes)
