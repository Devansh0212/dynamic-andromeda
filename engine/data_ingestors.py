import os
import requests
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime

class DataIngestor:
    """Base class for data ingestion."""
    def fetch_series(self, series_id: str, start_date: str) -> pd.DataFrame:
        raise NotImplementedError

class FredIngestor(DataIngestor):
    """Ingests economic data from the Federal Reserve Economic Data (FRED) API."""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            print("WARNING: No FRED_API_KEY provided. Ingestor will fail unless mocked.")

    def fetch_series(self, series_id: str, start_date: str = "1960-01-01") -> pd.DataFrame:
        """
        Fetches a time series from FRED.
        Returns a DataFrame with 'date' and 'value'.
        """
        if not self.api_key:
             # Return mock data for demonstration if no key
            print(f"returning mock data for {series_id}")
            return self._generate_mock_data(series_id, start_date)

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            df = pd.DataFrame(observations)
            
            if df.empty:
                return pd.DataFrame(columns=["date", "value"])
                
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df[["date", "value"]].dropna().set_index("date")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {series_id}: {e}")
            return pd.DataFrame(columns=["date", "value"])

    def _generate_mock_data(self, series_id: str, start_date: str) -> pd.DataFrame:
        """Generates realistic-looking mock data for testing without API key."""
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='M')
        # Simple random walk
        import numpy as np
        np.random.seed(42) # Deterministic mock
        values = np.random.randn(len(dates)).cumsum() + 100
        return pd.DataFrame({'value': values}, index=dates)

class Pipeline:
    def __init__(self):
        self.ingestor = FredIngestor()
        
    def run_daily_ingest(self):
        # Core 4 data points for the Ray Model
        indicators = {
            "CPIAUCSL": "Inflation",      # CPI
            "GDPC1": "Growth",            # Real GDP
            "UNRATE": "Unemployment",     # Labor
            "FEDFUNDS": "Rates"           # Fed Funds
        }
        
        data_store = {}
        for series_id, name in indicators.items():
            print(f"Fetching {name} ({series_id})...")
            df = self.ingestor.fetch_series(series_id)
            data_store[name] = df
            
        return data_store

if __name__ == "__main__":
    # Test run
    p = Pipeline()
    data = p.run_daily_ingest()
    for k, v in data.items():
        print(f"{k}: {len(v)} records")
