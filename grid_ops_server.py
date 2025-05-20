#The MCP server provides tools and resources for grid operations research. Let's create a file
#named grid_ops_server.py:
"""
grid_ops_server.py - MCP Server for Grid Operations Research
This server provides tools and resources for grid operations research.

This server provides tools and resources for analyzing grid outages, monitoring data,
accessing research papers, and generating visualizations.
"""

import json
import os
import pandas as pd
import matplotlib
import numpy as np
import io
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# Set matplotlib backend before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Grid Operations Assistant")

# ----- Resources -----

@mcp.resource("grid://topology/{region}")
def get_grid_topology(region: str) -> Dict[str, Any]:
    """Retrieve power grid topology for a specific region."""
    topologies = {
        "northeast": {
            "voltage_levels": [345, 138, 69],  # kV
            "substations": 45,
            "transmission_lines": 1200,  # miles
            "primary_generators": ["Nuclear", "Hydro", "Wind"]
        },
        "southwest": {
            "voltage_levels": [500, 230, 115],
            "substations": 32,
            "transmission_lines": 950,
            "primary_generators": ["Solar", "Natural Gas", "Coal"]
        }
    }
    return topologies.get(region.lower(), {"error": f"Topology for {region} not found"})

@mcp.resource("grid://load/{dataset_id}")
def get_grid_load_data(dataset_id: str) -> Dict[str, Any]:
    """Retrieve grid load dataset by ID."""
    datasets = {
        "peak_load_2023": {
            "name": "Regional Peak Load Analysis",
            "source": "NERC",
            "time_range": "2023",
            "unit": "MW",
            "data": {
                "regions": ["Northeast", "Southeast", "Midwest", "West"],
                "peak_loads": [65000, 72000, 58000, 48000]
            }
        },
        "hourly_load": {
            "name": "Hourly Load Profile",
            "source": "ISO-NE",
            "time_range": "2024-01-01 to 2024-01-07",
            "unit": "MW",
            "data": {
                "hours": list(range(24)),
                "load": [np.random.normal(15000, 2000) for _ in range(24)]
            }
        }
    }
    return datasets.get(dataset_id, {"error": f"Dataset {dataset_id} not found"})

# ----- Tools -----

@mcp.tool()
def analyze_load_pattern(dataset_id: str, window_hours: int = 24) -> Dict[str, Any]:
    """Analyze load patterns in grid data."""
    data = get_grid_load_data(dataset_id)
    
    if "error" in data:
        return data
    
    df = pd.DataFrame(data["data"])
    df['load'] = df['load'].rolling(window=window_hours).mean()
    
    return {
        "dataset": data["name"],
        "analysis_window": f"{window_hours}h",
        "max_load": round(df['load'].max(), 2),
        "min_load": round(df['load'].min(), 2),
        "avg_load": round(df['load'].mean(), 2),
        "trend": "stable" if df['load'].std() < 1000 else "volatile"
    }

@mcp.tool()
def predict_outage_risk(equipment_id: str, weather_data: Dict[str, float]) -> Dict[str, Any]:
    """Predict outage risk for grid equipment based on weather conditions."""
    # Simulated risk model
    base_risk = 0.05
    risk_factors = {
        "temperature": 0.001 * abs(weather_data.get("temp_c", 25) - 25),
        "wind_speed": 0.002 * weather_data.get("wind_kph", 0),
        "precipitation": 0.003 * weather_data.get("precip_mm", 0)
    }
    
    total_risk = base_risk + sum(risk_factors.values())
    
    return {
        "equipment_id": equipment_id,
        "risk_score": round(total_risk, 4),
        "risk_category": "high" if total_risk > 0.1 else "medium" if total_risk > 0.05 else "low",
        "factors": risk_factors
    }

@mcp.tool()
def generate_grid_visualization(dataset_id: str) -> Dict[str, Any]:
    """Generate visualization of grid operational data."""
    data = get_grid_load_data(dataset_id)
    
    plt.figure(figsize=(10, 6))
    
    if "hours" in data["data"]:
        plt.plot(data["data"]["hours"], data["data"]["load"], 'b-', linewidth=2)
        plt.title("Hourly Load Profile")
        plt.xlabel("Hour of Day")
        plt.ylabel("Load (MW)")
    elif "regions" in data["data"]:
        plt.bar(data["data"]["regions"], data["data"]["peak_loads"])
        plt.title("Regional Peak Loads")
        plt.ylabel("Peak Load (MW)")
    
    plt.grid(True, linestyle='--', alpha=0.7)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    
    return {
        "visualization": f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}",
        "dataset": data["name"]
    }

# ----- Server Execution -----

if __name__ == "__main__":
    print("GridOperationsServer:STARTED", flush=True)
    mcp.run(transport='stdio')
