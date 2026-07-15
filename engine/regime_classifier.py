import pandas as pd
import numpy as np
from typing import Dict, Tuple

class RegimeClassifier:
    """Classifies the economic environment into one of 4 regimes based on Growth and Inflation."""
    
    REGIMES = {
        (True, True): "Reflation/Boom (Growth+, Inflation+)", # Q2
        (True, False): "Goldilocks (Growth+, Inflation-)",    # Q1
        (False, True): "Stagflation (Growth-, Inflation+)",   # Q3
        (False, False): "Deflation/Bust (Growth-, Inflation-)" # Q4
    }

    def __init__(self, lookback_window: int = 12):
        self.lookback_window = lookback_window

    def calculate_trends(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates Year-over-Year change and Momentum.
        Expects a DataFrame with a single 'value' column.
        """
        df = data.copy()
        # YoY Change
        df['yoy'] = df['value'].pct_change(periods=12)
        # Momentum (Rate of Change of the Rate of Change) or Acceleration
        df['momentum'] = df['yoy'].diff()
        
        # Smooth out noise
        df['yoy_smooth'] = df['yoy'].rolling(window=3).mean()
        df['momentum_smooth'] = df['momentum'].rolling(window=3).mean()
        
        return df

    def classify(self, growth_data: pd.DataFrame, inflation_data: pd.DataFrame, date: str = None) -> Dict:
        """
        Determines the regime for a specific date (or latest if None).
        
        Args:
            growth_data: DataFrame of Growth Indicator (e.g., GDP/PMI)
            inflation_data: DataFrame of Inflation Indicator (e.g., CPI)
            date: ISO format date string
            
        Returns:
            Dict containing regime name, quadrant, and underlying metrics.
        """
        # Calculate derived metrics
        g_df = self.calculate_trends(growth_data)
        i_df = self.calculate_trends(inflation_data)
        
        # Align dates
        aligned = pd.merge(g_df, i_df, left_index=True, right_index=True, suffixes=('_growth', '_inflation'))
        
        if date:
            try:
                current = aligned.loc[date]
            except KeyError:
                # Find closest date
                idx = aligned.index.get_indexer([pd.to_datetime(date)], method='nearest')[0]
                current = aligned.iloc[idx]
        else:
            current = aligned.iloc[-1]
            
        # Logic: Is Growth Rising? Is Inflation Rising?
        # We look at the 'momentum' (2nd derivative) or just the trend of the YoY.
        # Simple Logic: Is YoY increasing vs last month?
        
        growth_rising = current['yoy_smooth_growth'] > aligned['yoy_smooth_growth'].shift(1).loc[current.name]
        inflation_rising = current['yoy_smooth_inflation'] > aligned['yoy_smooth_inflation'].shift(1).loc[current.name]
        
        regime_key = (growth_rising, inflation_rising)
        regime_name = self.REGIMES.get(regime_key, "Unknown")
        
        return {
            "date": str(current.name.date()),
            "regime": regime_name,
            "details": {
                "growth_yoy": round(current['yoy_growth'], 4),
                "growth_rising": bool(growth_rising),
                "inflation_yoy": round(current['yoy_inflation'], 4),
                "inflation_rising": bool(inflation_rising)
            }
        }

if __name__ == "__main__":
    # Test stub
    rc = RegimeClassifier()
    
    # Mock aligned data
    dates = pd.date_range("2020-01-01", "2023-01-01", freq="M")
    growth_vals = np.linspace(100, 110, len(dates)) + np.random.normal(0, 1, len(dates)) # General up trend
    inflation_vals = np.linspace(200, 220, len(dates)) # High inflation
    
    g_df = pd.DataFrame({'value': growth_vals}, index=dates)
    i_df = pd.DataFrame({'value': inflation_vals}, index=dates)
    
    result = rc.classify(g_df, i_df)
    print(f"Latest Regime: {result}")
