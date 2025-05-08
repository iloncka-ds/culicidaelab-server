import solara

# --- Filter States ---
selected_species_reactive = solara.reactive([])
# Using Tuple for date range
selected_date_range_reactive = solara.reactive((None, None))
# Add more filters: e.g., data source, region
selected_region_reactive = solara.reactive(None)
selected_data_source_reactive = solara.reactive(None)


# --- Layer Visibility ---
show_observed_data_reactive = solara.reactive(True)
show_modeled_data_reactive = solara.reactive(False)  # Default off as it can be heavy
show_distribution_status_reactive = solara.reactive(True)
show_breeding_sites_reactive = solara.reactive(False)  # From map DETAILED PLAN

# --- Map Interaction State ---
# For info panel when a feature (polygon, marker) is clicked
selected_map_feature_info = solara.reactive(None)
# To fetch data for current view, or trigger other actions on map move
current_map_bounds_reactive = solara.reactive(None)  # ((south, west), (north, east))
current_map_zoom_reactive = solara.reactive(None)

# --- Data States ---
# These would be populated by API calls. GeoJSON is a common format.
distribution_data_reactive = solara.reactive(None)  # GeoJSON dictionary
observations_data_reactive = solara.reactive(None)  # GeoJSON dictionary
modeled_data_reactive = solara.reactive(None)  # GeoJSON for heatmap/contours
breeding_sites_data_reactive = solara.reactive(None)  # GeoJSON for breeding sites

# Example: species_list_reactive for populating filters, fetched from API or config
all_available_species_reactive = solara.reactive(
    ["Aedes albopictus", "Aedes aegypti", "Culex pipiens"]
)  # Placeholder
all_available_regions_reactive = solara.reactive(["Europe", "Asia", "Africa"])  # Placeholder
all_available_data_sources_reactive = solara.reactive(
    ["GBIF", "User Uploads", "Scientific Study X"]
)  # Placeholder


# Loading states for different data types or general loading
data_loading_reactive = solara.reactive(False)  # General loading indicator for the map
distribution_loading_reactive = solara.reactive(False)
observations_loading_reactive = solara.reactive(False)
modeled_loading_reactive = solara.reactive(False)
breeding_sites_loading_reactive = solara.reactive(False)