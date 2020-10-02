import os
from sqlalchemy import create_engine
import pandas as pd


def clean_names(df):
    '''
    Input:
        df -> pd.DataFrame
            costar data with default costar data column names
    Output:
        df -> pd.DataFrame
            costar data with sanitized column names
    '''
    new_cols = [col.lower()
                .replace(r'$', '')
                .replace('%', 'pct')
                .replace(' ', '_')
                .replace('-', '_')
                .replace(r'/', '_')
                .replace('(', '')
                .replace(')', '') for col in list(df.columns.values)]

    df.columns = new_cols

    return df


def load_snapshot_data(path_to_costar_folder):
    '''
    Input:
        path_to_costar_folder -> str:
            file path to folder containing costar excel files
    Output:
        df -> pd.DataFrame
            binded dataframe of costar data
    '''
    full_paths = [os.path.join(path_to_costar_folder, file_path)
                  for file_path in os.listdir(path_to_costar_folder)]
    list_dfs = [pd.read_excel(f) for f in full_paths]
    df = pd.concat(list_dfs, axis=0, sort=False)
    df = clean_names(df)

    return df


if __name__ == "__main__":
    path_costar_folder = '../data/PDX-Multifamily/'
    df = load_snapshot_data(path_costar_folder)

    db_connection_url = "postgres://postgres:password@localhost:5432/shred"
    engine = create_engine(db_connection_url)

    df.to_sql('costar_multifamily_rent', con=engine, if_exists='replace', index=False)
