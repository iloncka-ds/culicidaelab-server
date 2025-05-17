# filter_panel.py
import solara
import datetime
from typing import cast, Optional, Dict, List, Any
import datetime as dt
from solara.alias import rv
import solara.lab
import httpx
import asyncio

# Relative imports
from frontend.state import (
    selected_species_reactive,
    all_available_species_reactive,
    selected_date_range_reactive,
    selected_region_reactive,
    all_available_regions_reactive,
    selected_data_source_reactive,
    all_available_data_sources_reactive,
    fetch_filter_options,
    distribution_data_reactive,
    observations_data_reactive,
    modeled_data_reactive,
    breeding_sites_data_reactive,
    distribution_loading_reactive,
    observations_loading_reactive,
    modeled_loading_reactive,
    breeding_sites_loading_reactive,
)
from frontend.config import (
    COLOR_BUTTON_PRIMARY_BG,
    FONT_BODY,
    SPECIES_DISTRIBUTION_ENDPOINT,
    OBSERVATIONS_ENDPOINT,
    MODELED_PROBABILITY_ENDPOINT,
    BREEDING_SITES_ENDPOINT,
)


async def fetch_data_with_filters():
    """Fetch data from all endpoints with applied filters"""
    # Build common filter parameters
    base_params = {}
    
    # Add species filter if any are selected
    if selected_species_reactive.value:
        base_params["species"] = ",".join(selected_species_reactive.value)
    
    # Add region filter if selected
    if selected_region_reactive.value:
        base_params["region"] = selected_region_reactive.value
    
    # Add data source filter if selected
    if selected_data_source_reactive.value:
        base_params["data_source"] = selected_data_source_reactive.value
    
    # Add date range filter if both start and end dates are selected
    start_date, end_date = selected_date_range_reactive.value
    if start_date and end_date:
        base_params["start_date"] = start_date.isoformat()
        base_params["end_date"] = end_date.isoformat()
    
    # Create tasks for all data fetching that needs to happen
    tasks = []
    
    # Fetch distribution data if visible
    from frontend.state import show_distribution_status_reactive
    if show_distribution_status_reactive.value:
        distribution_loading_reactive.value = True
        tasks.append(fetch_distribution_data(base_params))
    
    # Fetch observation data if visible
    from frontend.state import show_observed_data_reactive
    if show_observed_data_reactive.value:
        observations_loading_reactive.value = True
        tasks.append(fetch_observation_data(base_params))
    
    # Fetch modeled data if visible
    from frontend.state import show_modeled_data_reactive
    if show_modeled_data_reactive.value:
        modeled_loading_reactive.value = True
        tasks.append(fetch_modeled_data(base_params))
    
    # Fetch breeding sites data if visible
    from frontend.state import show_breeding_sites_reactive
    if show_breeding_sites_reactive.value:
        breeding_sites_loading_reactive.value = True
        tasks.append(fetch_breeding_sites_data(base_params))
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)


async def fetch_distribution_data(params: Dict[str, str]):
    """Fetch distribution data with applied filters"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SPECIES_DISTRIBUTION_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            distribution_data_reactive.value = response.json()
    except Exception as e:
        print(f"Error fetching distribution data: {e}")
        # Set to empty GeoJSON on error
        distribution_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        distribution_loading_reactive.value = False


async def fetch_observation_data(params: Dict[str, str]):
    """Fetch observation data with applied filters"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OBSERVATIONS_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            observations_data_reactive.value = response.json()
    except Exception as e:
        print(f"Error fetching observation data: {e}")
        # Set to empty GeoJSON on error
        observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        observations_loading_reactive.value = False


async def fetch_modeled_data(params: Dict[str, str]):
    """Fetch modeled data with applied filters"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(MODELED_PROBABILITY_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            modeled_data_reactive.value = response.json()
    except Exception as e:
        print(f"Error fetching modeled data: {e}")
        # Set to empty GeoJSON on error
        modeled_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        modeled_loading_reactive.value = False


async def fetch_breeding_sites_data(params: Dict[str, str]):
    """Fetch breeding sites data with applied filters"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BREEDING_SITES_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            breeding_sites_data_reactive.value = response.json()
    except Exception as e:
        print(f"Error fetching breeding sites data: {e}")
        # Set to empty GeoJSON on error
        breeding_sites_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        breeding_sites_loading_reactive.value = False


@solara.component
def FilterControls():
    # Ensure filter options are loaded
    loading_state = solara.use_reactive(False)
    
    # Effect to load filter options when component mounts
    solara.use_effect(
        lambda: asyncio.create_task(load_filter_options()),
        []  # Empty dependencies means this runs once on mount
    )
    
    async def load_filter_options():
        """Load filter options from the API"""
        if not loading_state.value:
            loading_state.value = True
            await fetch_filter_options()
            loading_state.value = False
    
    # Define callback for applying filters
    async def apply_filters():
        """Apply filters and fetch data"""
        await fetch_data_with_filters()

    # The card styling is better handled by ExpansionPanel in map_visualization.py
    # This component will just render the controls themselves.
    with solara.Column():
        if loading_state.value:
            solara.Info("Loading filter options...")
        
        # Species Filter
        solara.SelectMultiple(
            label="Select Mosquito Species",
            values=selected_species_reactive,
            all_values=all_available_species_reactive.value,
            dense=True,  # More compact
        )

        # Region Filter
        solara.Select(
            label="Select Region (Optional)",
            value=selected_region_reactive,
            values=[None] + all_available_regions_reactive.value,  # Allow unselecting
            dense=True,
        )

        # Data Source Filter
        solara.Select(
            label="Select Data Source (Optional)",
            value=selected_data_source_reactive,
            values=[None] + all_available_data_sources_reactive.value,
            dense=True,
        )

        # Date Range Filter using solara.lab.InputDateRange
        solara.Markdown("#### Date Range (Optional)")
        
        # Create a helper function to update selected_date_range_reactive
        def update_date_range(dates):
            selected_date_range_reactive.value = dates.value
        
        # Create the date range input
        dates = solara.use_reactive(selected_date_range_reactive.value)
        solara.lab.InputDateRange(
            dates,
            on_value=update_date_range,
        )

        # Add Apply Filters button
        solara.Button(
            "Apply Filters", 
            on_click=lambda: asyncio.create_task(apply_filters()),
            color=COLOR_BUTTON_PRIMARY_BG, 
            dark=True,
            style="margin-top: 15px;"
        )
        
        # Show loading state when filters are being applied
        if any([
            distribution_loading_reactive.value,
            observations_loading_reactive.value,
            modeled_loading_reactive.value,
            breeding_sites_loading_reactive.value
        ]):
            solara.Info("Applying filters and fetching data...")
