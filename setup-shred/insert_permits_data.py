from sqlalchemy import create_engine
import geopandas as gpd

db_connection_url = "postgres://postgres:password@localhost:5432/shred"
engine = create_engine(db_connection_url)

path_to_permits_data = '../data/Residential_Building_Permits.shp'
permits = gpd.read_file(path_to_permits_data)

# drop missing geometries
permits = permits[~permits['geometry'].isnull()]

permits.to_postgis('permits', con=engine, if_exists='replace', index=True)
