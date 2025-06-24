import pandas as pd
import numpy as np
from datetime import datetime

class CarbonBackend:
    def __init__(self):
        self.df = None
        self.co2_threshold = 1.0
        self.cpu_threshold = 80
        
    def load_data(self, file_path):
        """Load and preprocess data"""
        self.df = pd.read_csv(file_path)
        self._preprocess_data()
        return self.df
        
    def _preprocess_data(self):
        """Clean and prepare data"""
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Day'] = self.df['Date'].dt.day_name()
        self.df['Week'] = self.df['Date'].dt.isocalendar().week
        
    def get_filtered_data(self, date, locations):
        """Filter data based on user selection"""
        filtered = self.df[(self.df['Date'] == date) & 
                          (self.df['Data_Center_Location'].isin(locations))].copy()
        filtered['Threshold_Breach'] = filtered['Total_CO2_kg'].apply(
            lambda x: 'Yes' if x > self.co2_threshold else 'No')
        return filtered
        
    def get_summary_stats(self, filtered_data):
        """Calculate key metrics"""
        return {
            'total_co2': filtered_data['Total_CO2_kg'].sum(),
            'avg_cpu': filtered_data['CPU_Utilisation (%)'].mean(),
            'total_energy': filtered_data['Energy_Consumption_kWh'].sum(),
            'breach_count': (filtered_data['Threshold_Breach'] == 'Yes').sum()
        }
        
    def get_time_series(self):
        """Prepare time series data"""
        if self.df is None:
            return None
        return self.df.groupby('Date').agg({
            'Total_CO2_kg': 'sum',
            'Energy_Consumption_kWh': 'sum'
        }).reset_index()