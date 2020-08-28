from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd

db_connection_url = "postgres://postgres:password@localhost:5432/shred"
engine = create_engine(db_connection_url)

permits_query = '''SELECT * FROM permits;'''
permits = gpd.read_postgis(
    sql=permits_query,
    con=engine,
    geom_col='geometry',
    crs={'init': 'epsg:3857'}
)

permits = permits[permits['STATUS'] == 'Final']
permits = permits[permits['TYPE'].isin(['Single Family Dwelling', 'Accessory Dwelling Unit'])]
permits = permits[permits['WORK'].isin(['Alteration', 'New Construction', 'Addition'])]
permits = permits[permits['NEW_UNITS'] == 1]
permits = permits[~((permits['geometry'].isna()) | (permits['geometry'].is_empty))]

sfd_permits = permits[permits['TYPE'] == 'Single Family Dwelling'].copy()
adu_permits = permits[permits['TYPE'] == 'Accessory Dwelling Unit'].copy()

sfd_permits['adu_mentioned'] = sfd_permits['DESCRIPTION'].str.contains('ADU|Accessory Dwelling Unit', case=False)

sfd_permits = sfd_permits[sfd_permits['adu_mentioned']]
sfd_permits.drop('adu_mentioned', axis=1, inplace=True)

all_adu_permits = pd.concat([sfd_permits, adu_permits], axis=0)
all_adu_permits.reset_index(drop=True, inplace=True)
all_adu_permits.drop('index', axis=1, inplace=True)


all_adu_permits.to_postgis('adu_permits', con=engine, if_exists='replace', index=False)
