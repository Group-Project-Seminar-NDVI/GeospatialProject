from flask import Flask, jsonify, request
import psycopg2
import geopandas as gpd
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname='postgis_34_sample',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432'
)

# Define the API endpoint to fetch GeoJSON data based on year
@app.route('/api/data', methods=['GET'])
def get_geojson_data():
    year = request.args.get('year')
    if not year:
        return jsonify({'error': 'Year parameter is missing'}), 400
    
    # Execute SQL query to retrieve data for the selected year
    sql_query = f"SELECT id,area_m2,total_area, geometry FROM polygon_features WHERE year = '{year}'"
    gdf = gpd.read_postgis(sql_query, conn, geom_col='geometry')
    
    # Convert GeoDataFrame geometry to GeoJSON-like Python dictionaries
    gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.__geo_interface__)
    
    # Get the first 10 rows
    
    
    # Convert GeoDataFrame to GeoJSON format
    geojson_data = gdf.to_dict(orient='records')
    
    # Combine GeoJSON data and first 10 rows into a single dictionary
    response_data = {
        'geojson_data': geojson_data,
        
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
