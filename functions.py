import pandas as pd
import os

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