from os.path import join, expanduser
from sqlalchemy import create_engine
import geopandas as gpd

db_connection_url = "postgres://postgres:password@localhost:5432/shred"
engine = create_engine(db_connection_url)

path_to_rlis_folder = expanduser('~/RLIS/')

taxlots_folder = join(path_to_rlis_folder, 'TAXLOTS')
transit_folder = join(path_to_rlis_folder, 'TRANSIT')
streets_folder = join(path_to_rlis_folder, 'STREETS')
places_folder = join(path_to_rlis_folder, 'PLACES')
boundary_folder = join(path_to_rlis_folder, 'BOUNDARY')
land_folder = join(path_to_rlis_folder, 'LAND')

# TAXLOTS
taxlots = gpd.read_file(join(taxlots_folder, 'taxlots.shp'))
taxlots.to_postgis(name="taxlots", con=engine, if_exists='replace', index=False, index_label='TLID')

tl_many = gpd.read_file(join(taxlots_folder, 'tl_many.shp'))
tl_many.to_postgis(name='tl_many', con=engine, if_exists='replace', index=True)

# TRANSIT
lrt_stop = gpd.read_file(join(transit_folder, 'lrt_stop.shp'))
lrt_stop.to_postgis('lrt_stop', con=engine, if_exists='replace', index=True)

railroad = gpd.read_file(join(transit_folder, 'railroad.shp'))
railroad.to_postgis('railroad', con=engine, if_exists='replace', index=True)

parkride = gpd.read_file(join(transit_folder, 'parkride.shp'))
parkride.to_postgis('parkride', con=engine, if_exists='replace', index=True)

# STREETS
fwy = gpd.read_file(join(streets_folder, 'fwy.shp'))
fwy.to_postgis('fwy', con=engine, if_exists='replace', index=True

# PLACES
schools = gpd.read_file(join(places_folder, 'schools.shp'))
schools.to_postgis('schools', con=engine, if_exists='replace', index=True)

# BOUNDARY
school_district = gpd.read_file(join(boundary_folder, 'school_district.shp'))
school_district.to_postgis('school_district', con=engine, if_exists='replace', index=True)

# LAND
zoning = gpd.read_file(join(land_folder, 'zoning.shp'))
zoning.to_postgis('zoning', con=engine, if_exists='replace', index=True)

buildings = gpd.read_file(join(land_folder, 'buildings.shp'))
buildings.to_postgis('buildings', con=engine, if_exists='replace', index=True)

multifamily_housing_inventory = gpd.read_file(join(land_folder, 'multifamily_housing_inventory.shp'))
multifamily_housing_inventory.to_postgis('multifamily_housing_inventory', con=engine, if_exists='replace', index=True)
