from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from .ml_models import ml_engine

app = FastAPI(title="Crime Analyst AI API")

# Allow CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ForecastRequest(BaseModel):
    state_name: str
    target_crime: str = "Total Crimes"
    years_ahead: int = 5

@app.get("/")
def read_root():
    return {"message": "Crime Analyst AI API is running"}

@app.get("/api/states")
def get_states():
    """List all available states"""
    states = ml_engine.get_available_states()
    return {"states": states}

@app.get("/api/historical/{state_name}")
def get_historical(state_name: str):
    """Get raw historical data for a state"""
    data = ml_engine.get_historical_data(state_name)
    if not data:
        raise HTTPException(status_code=404, detail="State not found")
    return {"data": data}

@app.post("/api/forecast")
def get_forecast(req: ForecastRequest):
    """Get ML forecast for future years"""
    predictions = ml_engine.forecast_crime(
        req.state_name, 
        target_crime=req.target_crime, 
        years_ahead=req.years_ahead
    )
    if not predictions:
        raise HTTPException(status_code=400, detail="Could not generate forecast")
    return {"forecast": predictions}

@app.get("/api/insights/{state_name}")
def get_insights(state_name: str):
    """Get AI Actionable Insights for reducing crimes in a state"""
    recommendations = ml_engine.generate_ai_recommendations(state_name)
    if not recommendations:
         raise HTTPException(status_code=400, detail="Could not generate insights")
    return {"recommendations": recommendations}

@app.get("/api/clustering")
def get_clustering():
    """Get K-Means risk clustering for all states"""
    clusters = ml_engine.cluster_states_risk()
    if not clusters:
        raise HTTPException(status_code=400, detail="Could not generate clusters")
    return {"clusters": clusters}

@app.get("/api/geojson")
def get_geojson():
    """Serve the GeoJSON file for the map"""
    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "states_india (1).geojson")
    try:
        with open(geojson_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
