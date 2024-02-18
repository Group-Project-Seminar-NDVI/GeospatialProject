import webbrowser
import psycopg2
import geopandas as gpd
import folium

# Step 1: Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname='postgis_34_sample',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432'
)

# Step 2: Execute SQL query to select polygon features
sql_query = "SELECT * FROM polygon_features"

# Read the data from PostgreSQL into a GeoDataFrame
gdf = gpd.read_postgis(sql_query, conn, geom_col='geometry')

# Step 3: Calculate the extent of the GeoDataFrame
minx, miny, maxx, maxy = gdf.total_bounds
center = [(miny + maxy) / 2, (minx + maxx) / 2]

# Step 4: Get unique string values from the "year" column
unique_years = gdf['year'].unique()

# Step 5: Convert selected features to GeoJSON format
geojson_data = gdf.to_json()

# Step 6: Create a Leaflet map using Folium
mymap = folium.Map(location=center, zoom_start=10)

# Step 7: Add the GeoJSON data to the map as a GeoJSON layer
geojson_layer = folium.GeoJson(
    geojson_data,
    name='polygon_layer',  # Optional: name for the layer
    tooltip='{year}'  # Optional: tooltip
)
geojson_layer.add_to(mymap)

# Step 8: Add checkboxes for filtering data by year
checkboxes = ''.join([f'<input type="checkbox" id="{year}" onclick="updateData(\'{year}\')" checked><label for="{year}">{year}</label><br>' for year in unique_years])

# Step 9: Add JavaScript function to update map data based on checkbox selection
update_js = '''
<script>
function updateData(year) {
    var new_data = JSON.parse(JSON.stringify(geojson_data));
    var filtered_data = { "type": "FeatureCollection", "features": [] };
    for (var feature of new_data.features) {
        if (feature.properties.year === year) {
            filtered_data.features.push(feature);
        }
    }
    geojson_layer.clearLayers();
    L.geoJson(filtered_data).addTo(geojson_layer);
}
</script>
'''

# Step 10: Add checkboxes and JavaScript to the map
folium.Html(checkboxes + update_js, script=True).add_to(mymap)

# Step 11: Display the map in a new browser window
mymap.save("map.html")
webbrowser.open_new_tab("map.html")
