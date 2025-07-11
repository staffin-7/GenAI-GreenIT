import pandas as pd

class CarbonBackend:
    def __init__(self):
        self.df = None
        self.co2_threshold = 1.0
        self.cpu_threshold = 80

    def load_data(self, file_path):
        """Load and preprocess CSV data"""
        self.df = pd.read_csv(file_path)
        self._preprocess_data()

    def _preprocess_data(self):
        """Clean and enrich data"""
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Week'] = self.df['Date'].dt.isocalendar().week
        self.df['Day'] = self.df['Date'].dt.day_name()
        self.df['Threshold_Breach'] = self.df.apply(
            lambda row: 'Yes' if row['Total_CO2_kg'] > self.co2_threshold or row['CPU_Utilisation (%)'] > self.cpu_threshold else 'No',
            axis=1
        )

    def get_filtered_data(self, start_date=None, end_date=None, locations=None):
        """Filter by date range and locations, and re-apply breach logic"""
        filtered = self.df.copy()

        if start_date and end_date:
            filtered = filtered[
                (filtered['Date'].dt.date >= start_date) &
                (filtered['Date'].dt.date <= end_date)
            ]
        if locations:
            filtered = filtered[filtered['Data_Center_Location'].isin(locations)]

        # Recalculate breach based on current threshold values
        filtered['Threshold_Breach'] = filtered.apply(
            lambda row: 'Yes' if row['Total_CO2_kg'] > self.co2_threshold or row['CPU_Utilisation (%)'] > self.cpu_threshold else 'No',
            axis=1
        )
        return filtered


    def get_summary_stats(self, df):
        """Aggregate metrics for KPI cards"""
        if df.empty:
            return {
                'total_co2': 0,
                'avg_cpu': 0,
                'total_energy': 0,
                'breach_count': 0
            }
        return {
            'total_co2': df['Total_CO2_kg'].sum(),
            'avg_cpu': df['CPU_Utilisation (%)'].mean(),
            'total_energy': df['Energy_Consumption_kWh'].sum(),
            'breach_count': df[df['Threshold_Breach'] == 'Yes'].shape[0]
        }

    def get_time_series(self):
        """Prepare CO2 and energy trend over time"""
        if self.df is None or self.df.empty:
            return None
        return self.df.groupby('Date').agg({
            'Total_CO2_kg': 'sum',
            'Energy_Consumption_kWh': 'sum'
        }).reset_index()
