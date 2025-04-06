import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, TimestampedGeoJson
from datetime import datetime, timedelta
import random
import webbrowser
import os

# --- Simulation Parameters ---
NUM_ASSETS = 75
SIMULATION_DURATION_HOURS = 3
TIME_STEP_SECONDS = 30 # How often we record a position
# Approximate Bounding Box for Hampton Roads offshore area shown in original viz
LAT_BOUNDS = (36.85, 37.05)
LON_BOUNDS = (-76.4, -76.15)
ASSET_TYPES = ['Vessel', 'Personnel', 'Vehicle', 'Aircraft'] # Expanded types
AFFILIATIONS = ['Friend', 'Unknown', 'Neutral'] # Added Neutral
OUTPUT_CSV = 'simulated_disaster_response_data.csv'
OUTPUT_HTML = 'improved_disaster_response_map.html'

def simulate_data(num_assets, duration_hours, time_step_seconds, lat_bounds, lon_bounds):
    """Simulates GPS track data for multiple assets."""
    print(f"Simulating data for {num_assets} assets over {duration_hours} hours...")
    data = []
    start_time = datetime.now() - timedelta(hours=duration_hours)
    end_time = datetime.now()
    current_time = start_time

    asset_properties = {}
    for i in range(num_assets):
        asset_id = f"Asset_{i+1:03d}"
        asset_type = random.choice(ASSET_TYPES)
        affiliation = random.choice(AFFILIATIONS)
        # Start each asset at a random location
        lat = random.uniform(lat_bounds[0], lat_bounds[1])
        lon = random.uniform(lon_bounds[0], lon_bounds[1])
        # Simple random walk parameters (adjust step size for realism)
        lat_step = (lat_bounds[1] - lat_bounds[0]) * 0.005 # Smaller step size
        lon_step = (lon_bounds[1] - lon_bounds[0]) * 0.005
        asset_properties[asset_id] = {
            'type': asset_type,
            'affiliation': affiliation,
            'lat': lat,
            'lon': lon,
            'lat_step': lat_step,
            'lon_step': lon_step
        }

    # Simulate movement over time
    time_points = []
    temp_time = start_time
    while temp_time <= end_time:
        time_points.append(temp_time)
        temp_time += timedelta(seconds=time_step_seconds)

    for t in time_points:
        for asset_id, props in asset_properties.items():
            # Update position with random walk
            props['lat'] += np.random.normal(0, abs(props['lat_step']))
            props['lon'] += np.random.normal(0, abs(props['lon_step']))

            # Keep within bounds (simple reflection)
            if not (lat_bounds[0] <= props['lat'] <= lat_bounds[1]):
                props['lat'] = np.clip(props['lat'], lat_bounds[0], lat_bounds[1]) # Clip first
                props['lat_step'] *= -0.5 # Dampen reflection
            if not (lon_bounds[0] <= props['lon'] <= lon_bounds[1]):
                props['lon'] = np.clip(props['lon'], lon_bounds[0], lon_bounds[1]) # Clip first
                props['lon_step'] *= -0.5 # Dampen reflection

            data.append({
                'Timestamp': t.isoformat(),
                'AssetID': asset_id,
                'Latitude': props['lat'],
                'Longitude': props['lon'],
                'AssetType': props['type'],
                'Affiliation': props['affiliation']
            })

    df = pd.DataFrame(data)
    print(f"Simulation complete. Generated {len(df)} data points.")
    return df

def create_improved_map(df):
    """Creates an interactive Folium map with improvements."""
    print("Creating improved visualization...")

    if df.empty:
        print("DataFrame is empty. Cannot create map.")
        return None

    # Calculate map center
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='CartoDB positron')

    # --- Define Styling ---
    affiliation_colors = {
        'Friend': 'blue',
        'Unknown': 'red',
        'Neutral': 'gray'
    }
    type_icons = {
        'Vessel': 'ship',
        'Personnel': 'male',
        'Vehicle': 'truck',
        'Aircraft': 'plane'
    }

    # --- Layer for Clustered Markers (Latest Position) ---
    # Get the latest position for each asset
    latest_df = df.loc[df.groupby('AssetID')['Timestamp'].idxmax()]

    marker_cluster = MarkerCluster(name="Asset Locations (Latest)").add_to(m)

    for _, row in latest_df.iterrows():
        color = affiliation_colors.get(row['Affiliation'], 'black') # Default color
        icon_name = type_icons.get(row['AssetType'], 'question-circle') # Default icon

        # Create informative popup
        popup_html = f"""
        <b>ID:</b> {row['AssetID']}<br>
        <b>Type:</b> {row['AssetType']}<br>
        <b>Affiliation:</b> {row['Affiliation']}<br>
        <b>Time:</b> {row['Timestamp']}<br>
        <b>Coords:</b> ({row['Latitude']:.4f}, {row['Longitude']:.4f})
        """
        iframe = folium.IFrame(popup_html, width="200px", height="120px")
        popup = folium.Popup(iframe, max_width=250)

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            tooltip=f"{row['AssetID']} ({row['AssetType']})", # Tooltip on hover
            icon=folium.Icon(color=color, icon=icon_name, prefix='fa') # FontAwesome icons
        ).add_to(marker_cluster) # Add to cluster, not directly to map

    # --- Layer for Timestamped Tracks (Optional but powerful) ---
    # Prepare data for TimestampedGeoJson
    features = []
    for asset_id, group in df.groupby('AssetID'):
        props = group.iloc[0] # Get static properties from first record
        color = affiliation_colors.get(props['Affiliation'], 'black')
        icon_name = type_icons.get(props['AssetType'], 'question-circle')

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': group[['Longitude', 'Latitude']].values.tolist(),
            },
            'properties': {
                'times': group['Timestamp'].tolist(),
                 'style': { # Basic style for the line itself
                    'color': color,
                    'weight': 3,
                    'opacity': 0.6,
                },
                'icon': 'marker', # Use a generic marker for the point moving along line
                 'iconstyle': {
                     'icon': icon_name,
                     'iconSize': [20, 20],
                     'iconColor': 'white', # Color of the icon symbol itself
                     'markerColor': color, # Background color of the marker pin
                     'prefix': 'fa',
                 },
                 'popup': f"<b>ID:</b> {asset_id}<br><b>Type:</b> {props['AssetType']}<br><b>Affil:</b> {props['Affiliation']}",
                 'tooltip': f"{asset_id}"
            }
        })

    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='PT1M', # Aggregate updates to each minute on slider
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY-MM-DD HH:mm:ss',
        time_slider_drag_update=True,
        duration='PT1M', # How much time each step represents
        # name="Asset Tracks (Time Slider)"
    ).add_to(m)

    # --- Add Legend ---
    # Folium doesn't have a built-in dynamic legend, so we create HTML
    legend_html = '''
         <div style="position: fixed;
                     bottom: 50px; left: 50px; width: 180px; height: auto;
                     border:2px solid grey; z-index:9999; font-size:14px;
                     background-color:rgba(255, 255, 255, 0.8);
                     padding: 10px;
                     ">
         <b>Legend</b><br>
         <b>Affiliation:</b><br>
     '''
    for affiliation, color in affiliation_colors.items():
         legend_html += f'  <i class="fa fa-square" style="color:{color}"></i> {affiliation}<br>'

    legend_html += '<b>Asset Type (Icons):</b><br>'
    for asset_type, icon in type_icons.items():
        # Use a generic marker background for legend consistency
        legend_html += f'  <i class="fa fa-map-marker" style="color:grey"><i class="fa {icon}" style="color:white;font-size:0.8em;position:relative;top:-2px;left:-0.4px;"></i></i> {asset_type}<br>'
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))


    # --- Add Layer Control ---
    folium.LayerControl(collapsed=False).add_to(m)

    print(f"Map created. It will be saved to {OUTPUT_HTML}")
    return m

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Simulate Data
    simulated_df = simulate_data(
        num_assets=NUM_ASSETS,
        duration_hours=SIMULATION_DURATION_HOURS,
        time_step_seconds=TIME_STEP_SECONDS,
        lat_bounds=LAT_BOUNDS,
        lon_bounds=LON_BOUNDS
    )

    # 2. Save simulated data (optional)
    simulated_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Simulated data saved to {OUTPUT_CSV}")

    # 3. Create Improved Map
    map_object = create_improved_map(simulated_df)

    # 4. Save Map to HTML
    if map_object:
        map_object.save(OUTPUT_HTML)
        print(f"Interactive map saved to {OUTPUT_HTML}")

        # 5. Open the map in the default web browser (optional)
        try:
            filepath = 'file:///' + os.path.abspath(OUTPUT_HTML).replace('\\', '/')
            print(f"Attempting to open map at: {filepath}")
            webbrowser.open(filepath, new=2) # new=2: open in new tab if possible
        except Exception as e:
            print(f"Could not automatically open the map in browser: {e}")