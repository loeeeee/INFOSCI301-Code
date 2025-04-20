import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, TimestampedGeoJson, FeatureGroupSubGroup, Search
from datetime import datetime, timedelta
import random
import os
import pytz # For timezone handling if needed, though using naive datetime for simplicity here
import math # <--- ADD THIS IMPORT

# --- Simulation Parameters ---
# (Keep parameters as they were)
NUM_ASSETS = 75
SIMULATION_DURATION_HOURS = 3
TIME_STEP_SECONDS = 60 # Increased step for less overwhelming data
LAT_BOUNDS = (36.85, 37.05)
LON_BOUNDS = (-76.4, -76.15)
ASSET_TYPES = ['Vessel', 'Personnel', 'Vehicle', 'Aircraft']
AFFILIATIONS = ['Friend', 'Unknown', 'Neutral']
STATUS_OPTIONS = ['Active', 'Idle', 'Alert']
IDLE_THRESHOLD_METERS = 10
IDLE_PERIOD_STEPS = 3
ALERT_PROBABILITY = 0.01
PREDICTION_STEPS = 3
OUTPUT_CSV = 'simulated_disaster_response_data_v2.csv'
OUTPUT_HTML = 'improved_disaster_response_map_v2.html'


# --- ADD THIS HAVERSINE FUNCTION ---
def haversine(coord1, coord2):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees).
    """
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371000  # Radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # Output distance in meters
    return meters
# --- END OF HAVERSINE FUNCTION ---


def get_asset_properties(num_assets, lat_bounds, lon_bounds):
    """Initializes static and dynamic properties for assets."""
    # (This function remains the same)
    asset_properties = {}
    for i in range(num_assets):
        asset_id = f"Asset_{i+1:03d}"
        asset_type = random.choice(ASSET_TYPES)
        affiliation = random.choice(AFFILIATIONS)
        lat = random.uniform(lat_bounds[0], lat_bounds[1])
        lon = random.uniform(lon_bounds[0], lon_bounds[1])
        lat_step = (lat_bounds[1] - lat_bounds[0]) * 0.003
        lon_step = (lon_bounds[1] - lon_bounds[0]) * 0.003
        asset_properties[asset_id] = {
            'type': asset_type,
            'affiliation': affiliation,
            'lat': lat,
            'lon': lon,
            'lat_step': lat_step,
            'lon_step': lon_step,
            'status': 'Active',
            'history': [],
            'last_significant_move_time': datetime.min
        }
    return asset_properties

def update_asset_state(asset_id, props, t, time_step_seconds, lat_bounds, lon_bounds):
    """Updates a single asset's position and status for a time step."""
    old_lat, old_lon = props['lat'], props['lon']

    # Update position (same as before)
    props['lat'] += np.random.normal(0, abs(props['lat_step']))
    props['lon'] += np.random.normal(0, abs(props['lon_step']))
    props['lat'] = np.clip(props['lat'], lat_bounds[0], lat_bounds[1])
    props['lon'] = np.clip(props['lon'], lon_bounds[0], lon_bounds[1])

    # Store history (same as before)
    props['history'].append((props['lat'], props['lon']))
    if len(props['history']) > IDLE_PERIOD_STEPS + 1:
        props['history'].pop(0)

    # --- Update Status ---
    # Check for movement using the new haversine function
    # MODIFY THIS LINE: Remove '* 1000' as our function returns meters directly
    moved_distance = haversine((old_lon, old_lat), (props['lon'], props['lat'])) # Pass (lon, lat) tuples

    if moved_distance > IDLE_THRESHOLD_METERS / 2:
         props['status'] = 'Active'
         props['last_significant_move_time'] = t
    else:
        if len(props['history']) > IDLE_PERIOD_STEPS:
             max_hist_dist = 0
             current_pos = props['history'][-1]
             for hist_pos in props['history'][-IDLE_PERIOD_STEPS-1:-1]:
                  # Use the new haversine here too
                  dist = haversine((current_pos[1], current_pos[0]), (hist_pos[1], hist_pos[0]))
                  max_hist_dist = max(max_hist_dist, dist)

             if max_hist_dist < IDLE_THRESHOLD_METERS:
                  props['status'] = 'Idle'
             else:
                 props['status'] = 'Active'

    # Random chance of alert (same as before)
    if props['status'] == 'Active' and random.random() < ALERT_PROBABILITY:
        props['status'] = 'Alert'

    return {
        'Timestamp': t.isoformat(),
        'AssetID': asset_id,
        'Latitude': props['lat'],
        'Longitude': props['lon'],
        'AssetType': props['type'],
        'Affiliation': props['affiliation'],
        'Status': props['status']
    }

# --- simulate_data_v2 function remains the same ---
def simulate_data_v2(num_assets, duration_hours, time_step_seconds, lat_bounds, lon_bounds):
    """Simulates GPS track data with status updates."""
    print(f"Simulating data for {num_assets} assets over {duration_hours} hours...")
    data = []
    start_time = datetime.now() - timedelta(hours=duration_hours)
    end_time = datetime.now()

    asset_properties = get_asset_properties(num_assets, lat_bounds, lon_bounds)

    current_time = start_time
    while current_time <= end_time:
        for asset_id, props in asset_properties.items():
            data.append(update_asset_state(asset_id, props, current_time, time_step_seconds, lat_bounds, lon_bounds))
        current_time += timedelta(seconds=time_step_seconds)

    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    print(f"Simulation complete. Generated {len(df)} data points.")
    return df


# --- create_improved_map_v2 function remains the same ---
# (No changes needed within this function itself, as it relies on the data generated previously)
def create_improved_map_v2(df):
    """Creates an interactive Folium map addressing feedback."""
    print("Creating improved visualization v2...")
    # ... (rest of the function is identical to the previous version) ...
    if df.empty:
        print("DataFrame is empty. Cannot create map.")
        return None

    # Calculate map center and ensure Timestamp is sorted per asset
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    df = df.sort_values(by=['AssetID', 'Timestamp'])

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='CartoDB positron')

    # --- Define Styling ---
    affiliation_colors = {'Friend': 'blue', 'Unknown': 'red', 'Neutral': 'gray'}
    type_icons = {'Vessel': 'ship', 'Personnel': 'male', 'Vehicle': 'truck', 'Aircraft': 'plane'}
    status_colors = {'Active': 'green', 'Idle': 'orange', 'Alert': 'purple'} # Use for outline or variation

    # --- Layers for Filtering (Latest Position) ---
    latest_df = df.loc[df.groupby('AssetID')['Timestamp'].idxmax()]

    # Create parent FeatureGroups for LayerControl structure
    latest_positions_group = folium.FeatureGroup(name="Latest Positions (Filterable)", show=True).add_to(m)
    affiliation_groups = {}
    type_groups = {}

    # Create sub-groups for affiliations
    for affiliation in AFFILIATIONS:
        color = affiliation_colors[affiliation]
        affiliation_groups[affiliation] = FeatureGroupSubGroup(
            latest_positions_group, f'<span style="color:{color};">Affil: {affiliation}</span>', show=True
        ).add_to(m)

    # Create sub-groups for types
    type_parent_group = folium.FeatureGroup(name="Filter by Type", show=False).add_to(m) # Initially hidden
    for asset_type in ASSET_TYPES:
         type_groups[asset_type] = FeatureGroupSubGroup(
             type_parent_group, f'Type: {asset_type}', show=True # Show subgroup if parent is shown
         ).add_to(m)

    # --- Add Markers to Filterable Layers ---
    markers = [] # For search plugin
    for _, row in latest_df.iterrows():
        affiliation = row['Affiliation']
        asset_type = row['AssetType']
        status = row['Status']

        base_color = affiliation_colors.get(affiliation, 'black')
        icon_name = type_icons.get(asset_type, 'question-circle')
        status_indicator_color = status_colors.get(status, 'white')

        # Richer Tooltip & Popup (same as before)
        tooltip_html = f"""
        <b>ID:</b> {row['AssetID']} | <b>Type:</b> {asset_type}<br>
        <b>Affil:</b> {affiliation} | <b>Status:</b> <span style='color:{status_indicator_color}; font-weight:bold;'>{status}</span><br>
        <b>Time:</b> {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        """
        popup_html = f"""
        <b>Asset Details</b><hr>
        <b>ID:</b> {row['AssetID']}<br>
        <b>Type:</b> {asset_type}<br>
        <b>Affiliation:</b> {affiliation}<br>
        <b>Status:</b> <span style='color:{status_indicator_color}; font-weight:bold;'>{status}</span><br>
        <b>Last Seen:</b> {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Coords:</b> ({row['Latitude']:.5f}, {row['Longitude']:.5f})
        """
        iframe = folium.IFrame(popup_html, width="230px", height="160px")
        popup = folium.Popup(iframe, max_width=300)

        marker_color = base_color
        if status == 'Alert': marker_color = 'purple'
        elif status == 'Idle': marker_color = 'orange'

        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            tooltip=tooltip_html,
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix='fa')
        )

        # Add to relevant filter groups
        marker.add_to(affiliation_groups[affiliation])
        marker_clone_for_type = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            tooltip=tooltip_html,
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix='fa')
        )
        marker_clone_for_type.add_to(type_groups[asset_type])

        # Add marker data to list for search plugin
        markers.append({
            "location": [row['Latitude'], row['Longitude']],
            "tooltip": f"{row['AssetID']} ({asset_type}, {affiliation}, {status})"
        })

    # Add Search plugin (same as before)
    search = Search(
        layer=latest_positions_group,
        search_label="tooltip",
        placeholder="Search Assets (ID, Type, Affil, Status)...",
        collapsed=True,
        position='topright',
    ).add_to(m)

    # --- Layer for Timestamped Tracks (same as before) ---
    features = []
    for asset_id, group in df.groupby('AssetID'):
        props = group.iloc[0]
        color = affiliation_colors.get(props['Affiliation'], 'black')
        icon_name = type_icons.get(props['AssetType'], 'question-circle')
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': group[['Longitude', 'Latitude']].values.tolist(),
            },
            'properties': {
                'times': group['Timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist(),
                 'style': {'color': color, 'weight': 2, 'opacity': 0.5},
                 'icon': 'marker',
                 'iconstyle': {
                     'icon': icon_name, 'iconSize': [20, 20], 'iconColor': 'white',
                     'markerColor': color, 'prefix': 'fa',
                 },
                 'popup': f"<b>Track:</b> {asset_id}<br><b>Type:</b> {props['AssetType']}",
                 'tooltip': f"Track: {asset_id}"
            }
        })
    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='PT1M', add_last_point=True, auto_play=False, loop=False, max_speed=10, loop_button=True,
        date_options='YYYY-MM-DD HH:mm:ss', time_slider_drag_update=True, duration='PT1M',
        # name="Asset Tracks (Time Slider)"
    ).add_to(m)

    # --- Layer for Predicted Paths (same as before) ---
    global TIME_STEP_SECONDS
    global LAT_BOUNDS
    global LON_BOUNDS
    prediction_group = folium.FeatureGroup(name="Predicted Paths (Next 3 Steps)", show=False).add_to(m)
    for asset_id, group in df.groupby('AssetID'):
        if len(group) < 2: continue
        last_point = group.iloc[-1]
        prev_point = group.iloc[-2]
        time_diff_sec = (last_point['Timestamp'] - prev_point['Timestamp']).total_seconds()
        if time_diff_sec == 0: continue

        lat_vel = (last_point['Latitude'] - prev_point['Latitude']) / time_diff_sec
        lon_vel = (last_point['Longitude'] - prev_point['Longitude']) / time_diff_sec

        current_lat, current_lon = last_point['Latitude'], last_point['Longitude']
        current_time = last_point['Timestamp']
        predicted_points = []
        predicted_line = [(current_lon, current_lat)]

        for i in range(PREDICTION_STEPS):
            pred_time = current_time + timedelta(seconds=TIME_STEP_SECONDS * (i + 1))
            pred_lat = current_lat + lat_vel * TIME_STEP_SECONDS * (i + 1)
            pred_lon = current_lon + lon_vel * TIME_STEP_SECONDS * (i + 1)
            pred_lat = np.clip(pred_lat, LAT_BOUNDS[0], LAT_BOUNDS[1])
            pred_lon = np.clip(pred_lon, LON_BOUNDS[0], LON_BOUNDS[1])
            predicted_points.append({'lat': pred_lat, 'lon': pred_lon, 'time': pred_time})
            predicted_line.append((pred_lon, pred_lat))

            folium.CircleMarker(
                location=[pred_lat, pred_lon], radius=4, color='magenta',
                fill=True, fill_opacity=0.6 - i * 0.1,
                popup=f"Predicted: {asset_id}<br>Time: {pred_time.strftime('%H:%M:%S')}",
                tooltip=f"Pred. Step {i+1}"
            ).add_to(prediction_group)

        folium.PolyLine(
            locations=[(p['lat'], p['lon']) for p in [{'lat': last_point['Latitude'], 'lon': last_point['Longitude']}] + predicted_points],
            color='magenta', weight=2, opacity=0.7, dash_array='5, 5'
        ).add_to(prediction_group)

    # --- Add Legend (Updated - same as before) ---
    legend_html = '''
         <div style="position: fixed;
                     bottom: 50px; left: 10px; width: auto; height: auto; max-width: 200px;
                     border:2px solid grey; z-index:9999; font-size:12px;
                     background-color:rgba(255, 255, 255, 0.85);
                     padding: 8px; border-radius: 5px;
                     ">
         <b style="font-size:14px;">Legend</b><br>
         <b>Affiliation:</b><br>
     '''
    for affiliation, color in affiliation_colors.items(): legend_html += f'  <i class="fa fa-square" style="color:{color}"></i> {affiliation}<br>'
    legend_html += '<b>Asset Type (Icon):</b><br>'
    for asset_type, icon in type_icons.items(): legend_html += f'  <i class="fa fa-map-marker" style="color:grey; position:relative;"><i class="fa {icon}" style="color:white; font-size:0.8em; position:absolute; top:3px; left:4px;"></i></i> {asset_type}<br>'
    legend_html += '<b>Status (Marker Color):</b><br>'
    legend_html += f'  <i class="fa fa-circle" style="color:{status_colors["Alert"]}"></i> Alert<br>'
    legend_html += f'  <i class="fa fa-circle" style="color:{status_colors["Idle"]}"></i> Idle<br>'
    legend_html += f'  <span style="font-style: italic;">(Affiliation color if Active)</span><br>'
    legend_html += '<b>Prediction:</b><br>'
    legend_html += f'  <i class="fa fa-circle" style="color:magenta"></i>/<span style="color:magenta;font-weight:bold;">---</span> Path<br>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    # --- Add Layer Control (same as before) ---
    folium.LayerControl(collapsed=False).add_to(m)

    print(f"Map created. It will be saved to {OUTPUT_HTML}")
    return m


# --- Main Execution (remains the same) ---
if __name__ == "__main__":
    # 1. Simulate Data
    simulated_df = simulate_data_v2(
        num_assets=NUM_ASSETS,
        duration_hours=SIMULATION_DURATION_HOURS,
        time_step_seconds=TIME_STEP_SECONDS,
        lat_bounds=LAT_BOUNDS,
        lon_bounds=LON_BOUNDS
    )

    # 2. Save simulated data
    simulated_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Simulated data saved to {OUTPUT_CSV}")

    # 3. Create Improved Map
    map_object = create_improved_map_v2(simulated_df)

    # 4. Save Map to HTML
    if map_object:
        map_object.save(OUTPUT_HTML)
        print(f"Interactive map saved to {OUTPUT_HTML}")
