import psycopg2
import osgeo.ogr
import shapely
import shapely.wkt
import geopandas as gpd

DATABASE = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'password',
    'database': 'shred'
}


con = psycopg2.connect(
    database=DATABASE['database'],
    user=DATABASE['user'],
    password=DATABASE['password'],
    host=DATABASE['host'],
    port=DATABASE['port']
    )

cur = con.cursor()

# execute sql commands below
cur.execute('''select version();''')


con.commit()
con.close()
