import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------------
# 1) Page Setup: White background, custom title
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="Project Delivery Group - GoTriangle Bus Stop Improvement Program",
    layout="wide"
)

# Force a white background, black text, and highlight the image expand icon
st.markdown("""
    <style>
    .main, .block-container {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    button[data-testid="stImageExpandButton"] {
        background-color: yellow !important;
        border: 2px solid red !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 2) Load Excel from Dropbox, auto-detect header row (CACHED)
# -------------------------------------------------------------------------
excel_url = "https://www.dropbox.com/scl/fi/y9e6id2kf1o9j3r0rnsqu/Group-C-H.xlsx?rlkey=i8fh3z6bxmczoa53myi9wgk7c&st=ke57by4o&dl=1"

@st.cache_data  # <-- This decorator enables caching for data
def load_excel_with_auto_header(url):
    for potential_header in range(6):
        df_try = pd.read_excel(url, engine="openpyxl", header=potential_header)
        df_try.columns = [col.strip() for col in df_try.columns]
        if "West [X]" in df_try.columns and "North [Y]" in df_try.columns:
            df_try["West [X]"] = pd.to_numeric(df_try["West [X]"], errors="coerce")
            df_try["North [Y]"] = pd.to_numeric(df_try["North [Y]"], errors="coerce")
            return df_try
    raise ValueError("Could not find 'West [X]' and 'North [Y]' in any header row (0..5).")

df = load_excel_with_auto_header(excel_url)

# -------------------------------------------------------------------------
# 3) Detect status column, fallback if not found
# -------------------------------------------------------------------------
def find_status_column(df):
    for col in df.columns:
        if "status" in col.lower() or "non-compliant" in col.lower():
            return col
    return None

status_col = find_status_column(df)
if not status_col:
    status_col = "Unknown Status"
    df[status_col] = "Unknown"

# -------------------------------------------------------------------------
# 4) Marker color logic for map
# -------------------------------------------------------------------------
def get_marker_color(status_value):
    if not isinstance(status_value, str):
        return "blue"
    s_lower = status_value.lower()
    if "non-compliant" in s_lower:
        return "red"
    elif "incomplete" in s_lower:
        return "orange"
    elif "in construction" in s_lower:
        return "blue"
    else:
        return "green"

# -------------------------------------------------------------------------
# 5) Functions to create maps using different base map styles
# -------------------------------------------------------------------------
def create_map_osm(df, status_col):
    if df.empty:
        return folium.Map(location=[37.0, -95.0], zoom_start=4, tiles="OpenStreetMap")
    df = df.dropna(subset=["West [X]", "North [Y]"]).copy()
    df["Longitude"] = -df["West [X]"]
    df["Latitude"]  = df["North [Y]"]
    avg_lat = df["Latitude"].mean()
    avg_lon = df["Longitude"].mean()

    folium_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="OpenStreetMap")
    for _, row in df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        stop_name = row.get("Stop Name", "Unknown Stop")
        bus_id = row.get("Bus stop Number", "N/A")
        status_val = row.get(status_col, "Unknown")

        popup_html = f"""
        <b>Stop Name:</b> {stop_name}<br>
        <b>Bus stop Number:</b> {bus_id}<br>
        <b>Status:</b> {status_val}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=f"Bus ID: {bus_id}",
            icon=folium.Icon(color=get_marker_color(status_val), icon="bus", prefix="fa")
        ).add_to(folium_map)
    return folium_map

def create_map_cartodb(df, status_col):
    if df.empty:
        return folium.Map(location=[37.0, -95.0], zoom_start=4, tiles="CartoDB positron")
    df = df.dropna(subset=["West [X]", "North [Y]"]).copy()
    df["Longitude"] = -df["West [X]"]
    df["Latitude"]  = df["North [Y]"]
    avg_lat = df["Latitude"].mean()
    avg_lon = df["Longitude"].mean()

    folium_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="CartoDB positron")
    for _, row in df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        stop_name = row.get("Stop Name", "Unknown Stop")
        bus_id = row.get("Bus stop Number", "N/A")
        status_val = row.get(status_col, "Unknown")

        popup_html = f"""
        <b>Stop Name:</b> {stop_name}<br>
        <b>Bus stop Number:</b> {bus_id}<br>
        <b>Status:</b> {status_val}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=f"Bus ID: {bus_id}",
            icon=folium.Icon(color=get_marker_color(status_val), icon="bus", prefix="fa")
        ).add_to(folium_map)
    return folium_map

def create_map_esri_street(df, status_col):
    if df.empty:
        return folium.Map(location=[37.0, -95.0], zoom_start=4, tiles=None)
    df = df.dropna(subset=["West [X]", "North [Y]"]).copy()
    df["Longitude"] = -df["West [X]"]
    df["Latitude"]  = df["North [Y]"]
    avg_lat = df["Latitude"].mean()
    avg_lon = df["Longitude"].mean()

    folium_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles=None)
    esri_tiles = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri WorldStreetMap",
        name="Esri WorldStreetMap",
        overlay=False,
        control=True
    )
    esri_tiles.add_to(folium_map)

    for _, row in df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        stop_name = row.get("Stop Name", "Unknown Stop")
        bus_id = row.get("Bus stop Number", "N/A")
        status_val = row.get(status_col, "Unknown")
        popup_html = f"""
        <b>Stop Name:</b> {stop_name}<br>
        <b>Bus stop Number:</b> {bus_id}<br>
        <b>Status:</b> {status_val}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=f"Bus ID: {bus_id}",
            icon=folium.Icon(color=get_marker_color(status_val), icon="bus", prefix="fa")
        ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)
    return folium_map

def create_map_esri_imagery(df, status_col):
    if df.empty:
        return folium.Map(location=[37.0, -95.0], zoom_start=4, tiles=None)
    df = df.dropna(subset=["West [X]", "North [Y]"]).copy()
    df["Longitude"] = -df["West [X]"]
    df["Latitude"]  = df["North [Y]"]
    avg_lat = df["Latitude"].mean()
    avg_lon = df["Longitude"].mean()

    folium_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles=None)
    esri_imagery = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri WorldImagery",
        name="Esri WorldImagery",
        overlay=False,
        control=True
    )
    esri_imagery.add_to(folium_map)

    for _, row in df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        stop_name = row.get("Stop Name", "Unknown Stop")
        bus_id = row.get("Bus stop Number", "N/A")
        status_val = row.get(status_col, "Unknown")
        popup_html = f"""
        <b>Stop Name:</b> {stop_name}<br>
        <b>Bus stop Number:</b> {bus_id}<br>
        <b>Status:</b> {status_val}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=f"Bus ID: {bus_id}",
            icon=folium.Icon(color=get_marker_color(status_val), icon="bus", prefix="fa")
        ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)
    return folium_map

# -------------------------------------------------------------------------
# 6) Horizontal bar chart with color-coded bars
# -------------------------------------------------------------------------
def create_status_chart(df, status_col):
    status_counts = df[status_col].value_counts(dropna=False).reset_index()
    status_counts.columns = ["Status", "Count"]

    # Ensure "In Construction" is included
    if "In Construction" not in status_counts["Status"].values:
        extra_row = pd.DataFrame({"Status": ["In Construction"], "Count": [0]})
        status_counts = pd.concat([status_counts, extra_row], ignore_index=True)

    def chart_color_map(s):
        s_lower = s.lower()
        if "non-compliant" in s_lower:
            return "red"
        elif "incomplete" in s_lower:
            return "orange"
        elif "in construction" in s_lower:
            return "blue"
        else:
            return "green"
    status_counts["Color"] = status_counts["Status"].apply(chart_color_map)

    chart = (
        alt.Chart(status_counts)
        .mark_bar()
        .encode(
            y=alt.Y("Status:N", sort=None, title="Status"),
            x=alt.X("Count:Q", title="Count"),
            color=alt.Color("Color:N", scale=None),
            tooltip=["Status", "Count"]
        )
        .properties(width=700, height=300, title="Bus Stops by Status")
    )
    return chart

# -------------------------------------------------------------------------
# 7) Page Title
# -------------------------------------------------------------------------
st.title("GoTriangle Bus Stop Improvement Program")

############################################################################
# (A) ADD NEW FILTERS: Group Filter and Status Filter
############################################################################

# 1) Group Filter
if "Group" in df.columns:  # ensure the column name is exactly "Group"
    group_list = df["Group"].dropna().unique().tolist()
    group_list = ["(All Groups)"] + group_list
    selected_group = st.selectbox("Filter by Group:", group_list)
else:
    selected_group = "(All Groups)"  # fallback if "Group" col not found

# 2) Multi-Select Status Filter
status_list = df[status_col].dropna().unique().tolist()
status_list.sort()
selected_statuses = st.multiselect(
    "Filter by Status (choose one or more):",
    status_list,
    default=status_list
)

# 3) Apply the filters to 'df' BEFORE building the bus stop dropdown
df_filtered = df.copy()

if selected_group != "(All Groups)" and "Group" in df.columns:
    df_filtered = df_filtered[df_filtered["Group"] == selected_group]

if selected_statuses:
    df_filtered = df_filtered[df_filtered[status_col].isin(selected_statuses)]
else:
    df_filtered = df_filtered.iloc[0:0]

############################################################################
# (B) BUILD THE BUS STOP DROPDOWN in the SAME ORDER as in the Excel
#     plus "Group" appended to the label
############################################################################

df_filtered["combined_label"] = (
    df_filtered["Bus stop Number"].astype(str)
    + " - "
    + df_filtered["Stop Name"].astype(str)
)

if "Group" in df_filtered.columns:
    df_filtered["combined_label"] = (
        df_filtered["combined_label"]
        + " - Group "
        + df_filtered["Group"].astype(str)
    )

unique_labels_in_order = df_filtered["combined_label"].unique().tolist()
all_labels_new = ["(Show All)"] + unique_labels_in_order

selected_label = st.selectbox(
    "Search for a bus stop (type partial ID or Name):",
    all_labels_new
)

label_to_indices = {}
for idx, row in df_filtered.iterrows():
    label = row["combined_label"]
    label_to_indices.setdefault(label, []).append(idx)

if selected_label == "(Show All)":
    df_map = df_filtered
else:
    idx_list = label_to_indices.get(selected_label, [])
    df_map = df_filtered.loc[idx_list]

# -------------------------------------------------------------------------
# 8) Map Type Selection: Choose which base map to display
# -------------------------------------------------------------------------
map_options = ["OpenStreetMap", "CartoDB Positron", "ESRI WorldStreetMap", "ESRI WorldImagery"]
selected_map_type = st.selectbox("Select the base map type:", map_options)

if selected_map_type == "OpenStreetMap":
    folium_map = create_map_osm(df_map, status_col)
elif selected_map_type == "CartoDB Positron":
    folium_map = create_map_cartodb(df_map, status_col)
elif selected_map_type == "ESRI WorldStreetMap":
    folium_map = create_map_esri_street(df_map, status_col)
elif selected_map_type == "ESRI WorldImagery":
    folium_map = create_map_esri_imagery(df_map, status_col)
else:
    folium_map = create_map_osm(df_map, status_col)  # Fallback

# -------------------------------------------------------------------------
# 9) Layout: Map and Pictures
# -------------------------------------------------------------------------
col_map, col_pics = st.columns([3, 2], gap="medium")
with col_map:
    st_folium(folium_map, width=700, height=550)

# -------------------------------------------------------------------------
# 10) Pictures Section
# -------------------------------------------------------------------------
if "pic_index" not in st.session_state:
    st.session_state["pic_index"] = 0

with col_pics:
    st.subheader("Pictures")
    if selected_label == "(Show All)":
        st.write("Multiple stops selected. Please pick one bus stop to see pictures.")
    else:
        matched_indices = label_to_indices.get(selected_label, [])
        if len(matched_indices) == 0:
            st.write("No matching bus stop found.")
        elif len(matched_indices) > 1:
            st.write("Multiple stops match this name/ID. Please refine your selection.")
        else:
            row_index = matched_indices[0]
            row = df_filtered.loc[row_index]
            pics_str = str(row.get("Pictures", "")).strip()
            if not pics_str:
                st.write("No pictures available for this bus stop.")
            else:
                pic_urls = [x.strip() for x in pics_str.split(",")]
                if not pic_urls:
                    st.write("No pictures available for this bus stop.")
                else:
                    st.session_state["pic_index"] = min(
                        st.session_state["pic_index"],
                        len(pic_urls) - 1
                    )
                    current_pic_url = pic_urls[st.session_state["pic_index"]]
                    try:
                        # The built-in expand button is shown automatically
                        # because we pass the URL directly to st.image().
                        st.image(
                            current_pic_url,
                            width=350,
                            caption=f"Image {st.session_state['pic_index']+1} of {len(pic_urls)}"
                        )
                    except Exception as e:
                        st.error(f"Could not load image: {e}")
                    st.markdown(f"""
                        <a href="{current_pic_url}" download style="text-decoration:none; color:blue;">
                            Download
                        </a>
                    """, unsafe_allow_html=True)
                    col_btns = st.columns(2)
                    with col_btns[0]:
                        if st.button("Previous"):
                            st.session_state["pic_index"] = (
                                st.session_state["pic_index"] - 1
                            ) % len(pic_urls)
                    with col_btns[1]:
                        if st.button("Next"):
                            st.session_state["pic_index"] = (
                                st.session_state["pic_index"] + 1
                            ) % len(pic_urls)

# -------------------------------------------------------------------------
# 11) Status Chart
# -------------------------------------------------------------------------
st.markdown("### Status Chart")
chart = create_status_chart(df_filtered, status_col)
st.altair_chart(chart, use_container_width=False)

# -------------------------------------------------------------------------
# 12) Download a List of Bus Stops by Status
# -------------------------------------------------------------------------
st.markdown("### Download a List of Bus Stops by Status")

download_status_options = ["Non-Compliant", "Incomplete", "In Construction"]
download_selected_status = st.multiselect(
    "Select one or more statuses to download as CSV:",
    download_status_options
)

if download_selected_status:
    df_to_download = df_filtered[df_filtered[status_col].str.lower().isin(
        [s.lower() for s in download_selected_status]
    )]

    if df_to_download.empty:
        st.warning("No bus stops found for the selected status(es).")
    else:
        csv_data = df_to_download.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="selected_status_bus_stops.csv",
            mime="text/csv"
        )
