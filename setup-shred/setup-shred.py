import os
from sqlalchemy import create_engine
import geopandas as gpd

db_connection_url = "postgres://postgres:password@localhost:5432/shred"
engine = create_engine(db_connection_url)

path_to_rlis_folder = os.path.expanduser('~/RLIS/')

taxlots_folder = os.path.join(path_to_rlis_folder, 'TAXLOTS')
transit_folder = os.path.join(path_to_rlis_folder, 'TRANSIT')

taxlots = gpd.read_file(os.path.join(taxlots_folder, 'taxlots.shp'))
taxlots.to_postgis(name="taxlots", con=engine, if_exists='replace', index=False, index_label='TLID')

