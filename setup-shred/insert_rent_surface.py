from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from libpysal.cg.voronoi import voronoi_frames


# Functions
def crosswalk_buildings_to_block_groups(building_gdf, bg_gdf):
    gdf = gpd.sjoin(
        building_gdf, bg_gdf[['GEOID', 'geometry']], how='left', op='intersects')
    gdf = gdf.drop('index_right', axis=1)

    return gdf


def estimate_sq_miles_from_unprojected_polygon(bg_gdf):
    '''
    Input:
        bg_gdf -> gpd.GeoDataFrame
            spatial data frame of block groups that is projected, i.e. epsg corresponds to zone 10 or 11, units needs to be in meters
    Output:
        bg_gdf -> gpd.GeoDataFrame
            same data frame with the initial projection maintained but there is an additional `sq_miles` column which is the measured square miles of the census block group
    '''
    bg_gdf['sq_miles'] = bg_gdf.geometry.area / 2589988.1103

    return bg_gdf


def determine_dynamic_distance_threshold(bg_sq_miles, min_dist_threshold, max_dist_threshold, dist_scale_factor):
    derived_dist_factor = np.sqrt(bg_sq_miles) * dist_scale_factor
    if derived_dist_factor < min_dist_threshold:
        return min_dist_threshold
    elif derived_dist_factor > max_dist_threshold:
        return max_dist_threshold
    else:
        return derived_dist_factor


def average_rent_by_distance_band(
    building_gdf,
    rent_col,
    year_built_col,
    census_boundaries,
    min_dist_threshold,
    max_dist_threshold,
    dist_scale_factor,
    year_built_threshold,
    obs_threshold,
    n_top_rents
):
    tmp = pd.DataFrame(
        {rent_col: building_gdf[rent_col], year_built_col: building_gdf[year_built_col]}, index=building_gdf.index)
    avg_rents = []
    for index, row in census_boundaries.iterrows():
        tmp['dist'] = [(x.distance(row['geometry']) / 1609.34)
                       for x in building_gdf.geometry]
        dist_threshold = determine_dynamic_distance_threshold(
            bg_sq_miles=row['sq_miles'],
            min_dist_threshold=min_dist_threshold,
            max_dist_threshold=max_dist_threshold,
            dist_scale_factor=dist_scale_factor
        )

        query_1 = tmp[(tmp['dist'] < dist_threshold) & (
            tmp[year_built_col] >= year_built_threshold)]
        query_2 = tmp[tmp['dist'] < dist_threshold].sort_values(
            rent_col, ascending=False)

        if query_1.shape[0] >= obs_threshold:
            avg_rents.append(query_1[rent_col].mean())
        elif query_2.shape[0] >= obs_threshold:
            query_2 = query_2.iloc[0:n_top_rents, :]
            avg_rents.append(query_2[rent_col].mean())
        else:
            avg_rents.append(np.nan)

    return avg_rents


def compute_voronoi_from_costar_buildings(costar_gdf, bbox, rent_col):
    '''
    Input:
        costar_gdf -> gpd.GeoDataFrame
            geodataframe of costar snapshot data
        bbox -> gpd.GeoDataFrame
            geodataframe with single observation of bounding box to be used for voronoi process
        rent_col -> str
            name of column in costar data containing rent data that will be filtered to remove outliers
    Output:
        bbox_overlay -> gpd.GeoDataFrame
            geodataframe of voronoi shapes with the corresponding rent value assigned to each shape
    '''
    costar_gdf = costar_gdf.reset_index(drop=True)

    coordinates = np.vstack(
        (costar_gdf['longitude'], costar_gdf['latitude'])).T
    thiessens, points = voronoi_frames(coordinates)

    thiessens.crs = bbox.crs
    thiessens = thiessens.to_crs({'init': 'epsg:4269'})

    bbox_overlay = gpd.overlay(thiessens, bbox, how='intersection')
    bbox_overlay[rent_col] = costar_gdf[rent_col].values

    return bbox_overlay


def get_bg_avg_rent_from_voronoi(bg_, voronoi_, rent_col):
    t1 = gpd.sjoin(voronoi_, bg_)
    t2 = t1.groupby('GEOID').agg({rent_col: 'mean'}).reset_index()
    t3 = bg_.merge(t2, on='GEOID')
    return t3


if __name__ == "__main__":
    # I/O
    db_connection_url = "postgres://postgres:password@localhost:5432/shred"
    engine = create_engine(db_connection_url)

    costar_query = '''SELECT * FROM costar_multifamily_rent;'''

    df = pd.read_sql_query(
        sql=costar_query,
        con=engine
    )

    keepers = [
        'one_bedroom_asking_rent_sf',
        'two_bedroom_asking_rent_sf',
        'one_bedroom_asking_rent_unit',
        'two_bedroom_asking_rent_unit',
        'one_bedroom_avg_sf',
        'two_bedroom_avg_sf',
        'year_built',
        'latitude',
        'longitude',
        'number_of_units',
        'star_rating',
        'style',
        'building_class',
        'construction_material'
    ]

    # filter and select relevant observations
    pdx_mask = (df['county_name'] == 'Multnomah') & (df['city'] == 'Portland')
    pdx_df = df[pdx_mask].copy()

    affordability_mask = (
        (pdx_df['building_status'] == 'Existing')
        & (pdx_df['rent_type'] == 'Market')
        & (~pdx_df['affordable_type'].isin(['Rent Restricted', 'Rent Stabilized', 'Rent Subsidized', 'Affordable Units']))
        & (~pdx_df['university'].isin(['Portland State University', 'University of Portland']))
    )

    pdx_df = pdx_df[affordability_mask]
    pdx_df = pdx_df[keepers]

    drop_ = (
        (pdx_df['one_bedroom_asking_rent_unit'].isnull()) & (
            pdx_df['one_bedroom_asking_rent_sf'].isnull())
        & (pdx_df['two_bedroom_asking_rent_unit'].isnull()) & (pdx_df['two_bedroom_asking_rent_sf'].isnull())
    )

    pdx_df = pdx_df[~drop_]

    # convert to spatial
    coordinates = list(zip(pdx_df['longitude'], pdx_df['latitude']))
    geos = [Point(x, y) for x, y in coordinates]
    gdf = gpd.GeoDataFrame(pdx_df, geometry=geos)
    gdf.crs = {'init': 'epsg:4326'}

    county_shapes = gpd.read_file(
        'https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_county_500k.zip')

    multnomah_county_shape = county_shapes[(county_shapes['STATEFP'] == '41') & (
        county_shapes['NAME'] == 'Multnomah')]

    or_bg_ = gpd.read_file(
        'https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_41_bg_500k.zip')

    multnomah_county_bg = or_bg_[or_bg_['COUNTYFP'] == '051'].copy()
    multnomah_county_bg.to_crs(gdf.crs, inplace=True)
    gdf = crosswalk_buildings_to_block_groups(gdf, multnomah_county_bg)

    zone10_epsg = 26910
    gdf.to_crs(zone10_epsg, inplace=True)
    multnomah_county_bg.to_crs(zone10_epsg, inplace=True)

    multnomah_county_bg = estimate_sq_miles_from_unprojected_polygon(
        multnomah_county_bg)

    multnomah_county_bg_centroids = multnomah_county_bg.copy()
    multnomah_county_bg_centroids.geometry = multnomah_county_bg_centroids.centroid

    onebed = gdf[~gdf['one_bedroom_asking_rent_sf'].isnull()].copy()
    twobed = gdf[~gdf['two_bedroom_asking_rent_sf'].isnull()].copy()

    onebed_rents = average_rent_by_distance_band(
        building_gdf=onebed,
        rent_col='one_bedroom_asking_rent_sf',
        year_built_col='year_built',
        census_boundaries=multnomah_county_bg,
        dist_scale_factor=1,
        min_dist_threshold=0.25,
        max_dist_threshold=0.5,
        n_top_rents=3,
        obs_threshold=3,
        year_built_threshold=2010
    )

    twobed_rents = average_rent_by_distance_band(
        building_gdf=twobed,
        rent_col='two_bedroom_asking_rent_sf',
        year_built_col='year_built',
        census_boundaries=multnomah_county_bg,
        dist_scale_factor=1,
        min_dist_threshold=0.25,
        max_dist_threshold=0.5,
        n_top_rents=3,
        obs_threshold=3,
        year_built_threshold=2010
    )

    multnomah_county_bg['one_bed_rent_sf'] = onebed_rents
    multnomah_county_bg['two_bed_rent_sf'] = twobed_rents
    multnomah_county_bg.to_crs(epsg=4269, inplace=True)

    voronoi_one_bed = compute_voronoi_from_costar_buildings(
        onebed, multnomah_county_shape, 'one_bedroom_asking_rent_sf')

    voronoi_two_bed = compute_voronoi_from_costar_buildings(
        twobed, multnomah_county_shape, 'two_bedroom_asking_rent_sf')

    voronoi_one_bed = voronoi_one_bed[['one_bedroom_asking_rent_sf', 'geometry']]
    voronoi_two_bed = voronoi_two_bed[['two_bedroom_asking_rent_sf', 'geometry']]

    multnomah_county_bg = get_bg_avg_rent_from_voronoi(
        multnomah_county_bg, voronoi_one_bed, 'one_bedroom_asking_rent_sf')

    multnomah_county_bg = get_bg_avg_rent_from_voronoi(
        multnomah_county_bg, voronoi_two_bed, 'two_bedroom_asking_rent_sf')

    multnomah_county_bg['one_bed_rent_sf'] = multnomah_county_bg.apply(
        lambda x: x['one_bedroom_asking_rent_sf'] if np.isnan(x['one_bed_rent_sf']) else x['one_bed_rent_sf'], axis=1
    )

    multnomah_county_bg['two_bed_rent_sf'] = multnomah_county_bg.apply(
        lambda x: x['two_bedroom_asking_rent_sf'] if np.isnan(x['two_bed_rent_sf']) else x['two_bed_rent_sf'], axis=1
    )

    multnomah_county_bg = multnomah_county_bg[[
        'GEOID', 'one_bed_rent_sf', 'two_bed_rent_sf', 'geometry']]

    multnomah_county_bg.to_postgis('bg_rents', con=engine, if_exists='replace')
