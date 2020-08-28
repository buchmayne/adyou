from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd

db_connection_url = "postgres://postgres:password@localhost:5432/shred"
engine = create_engine(db_connection_url)

path_to_permits_data = '../data/Permit-Search-Results.csv'
permits = pd.read_csv(path_to_permits_data)

# convert to gdf
permits_gdf = gpd.GeoDataFrame(
    permits,
    geometry=gpd.points_from_xy(permits['X_WEB_MERCATOR'], permits['Y_WEB_MERCATOR']),
    crs={'init': 'epsg:3857'}
    )

# drop missing geometries
permits_gdf = permits_gdf[~permits_gdf['geometry'].isnull()]

permits_gdf.to_postgis('permits', con=engine, if_exists='replace', index=True)
