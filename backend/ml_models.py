import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Create path to data file, assuming the backend is running in the 'backend' folder
# The data file is in the parent directory
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "States10YearsFinal.csv")

class CrimeMLEngine:
    def __init__(self):
        try:
            self.df = pd.read_csv(DATA_PATH)
        except Exception as e:
            print(f"Error loading datasets: {e}")
            self.df = pd.DataFrame()
            
        self.crime_columns = [
            'Murders', 'Rape', 'Theft', 'Attempt to Commit Murder', 
            'Dacoity', 'Kidnapping & Abduction', 'Grievous Hurt', 
            'Burglary', 'Cybercrimes', 'Arson', 'Total Crimes'
        ]
        
        if not self.df.empty:
            for col in self.crime_columns + ['Projected Population', 'Year']:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
    def get_available_states(self):
        if self.df.empty: return []
        return sorted(self.df['State'].unique().tolist())
        
    def get_historical_data(self, state_name=None):
        if self.df.empty: return []
        data = self.df.copy()
        if state_name:
            data = data[data['State'] == state_name]
        return data.to_dict(orient='records')

    def forecast_crime(self, state_name, target_crime="Total Crimes", years_ahead=5):
        """
        Train a Linear Regression model to forecast a specific crime for future years.
        """
        if self.df.empty: return []
        
        state_data = self.df[self.df["State"] == state_name].copy()
        if state_data.empty: return []
        
        # Sort by year just in case
        state_data = state_data.sort_values(by="Year")
        
        X = state_data[["Year", "Projected Population"]].values
        y = state_data[target_crime].values
        
        # Only fit if we have enough data points
        if len(X) < 3:
            return []
            
        model = LinearRegression()
        model.fit(X, y)
        
        last_year = state_data["Year"].max()
        last_pop = state_data["Projected Population"].values[-1]
        
        # Assume population grows slightly. This is simplistic but works for demonstration.
        # Estimate population growth rate from history
        if len(state_data) >= 2:
            pop_growth = (state_data["Projected Population"].values[-1] - state_data["Projected Population"].values[0]) / len(state_data)
        else:
            pop_growth = 100000 
            
        forecasts = []
        for i in range(1, years_ahead + 1):
            future_year = last_year + i
            future_pop = last_pop + (pop_growth * i)
            
            # Predict
            pred_crime = model.predict([[future_year, future_pop]])[0]
            
            # Floor to 0
            pred_crime = max(0, int(pred_crime))
            
            forecasts.append({
                "Year": int(future_year),
                "Projected Population": float(future_pop),
                target_crime: pred_crime,
                "is_prediction": True
            })
            
        return forecasts

    def cluster_states_risk(self, target_year=2022):
        """
        Use K-Means to cluster states based on crime severity in a specific year.
        Categories: Low Risk, Medium Risk, High Risk
        """
        if self.df.empty: return {}
        
        year_data = self.df[self.df["Year"] == target_year].copy()
        if year_data.empty:
            year_data = self.df[self.df["Year"] == self.df["Year"].max()].copy()
            
        states = year_data["State"].values
        # We'll use the main crime columns per capita for a fair comparison
        X = year_data[self.crime_columns[:-1]].values # excluding total crimes
        populations = year_data["Projected Population"].values
        X_per_capita = (X / populations[:, np.newaxis]) * 100000
        
        # Scale data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_per_capita)
        
        # K-Means with 3 clusters
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Map cluster numbers to risk levels based on centroid magnitude
        cluster_magnitude = kmeans.cluster_centers_.sum(axis=1)
        sorted_clusters = np.argsort(cluster_magnitude)
        
        risk_mapping = {
            sorted_clusters[0]: "Low Risk",
            sorted_clusters[1]: "Medium Risk",
            sorted_clusters[2]: "High Risk"
        }
        
        results = []
        for i, state in enumerate(states):
            results.append({
                "State": state,
                "RiskLevel": risk_mapping[clusters[i]],
                "TotalCrimes": int(year_data.iloc[i]["Total Crimes"])
            })
            
        return results

    def generate_ai_recommendations(self, state_name):
        """
        Algorithmic insights: Find the fastest growing problem for a state and recommend policies.
        """
        if self.df.empty: return []
        
        state_data = self.df[self.df["State"] == state_name].sort_values(by="Year")
        if len(state_data) < 2: return []
        
        start_year = state_data.iloc[0]
        end_year = state_data.iloc[-1]
        
        fastest_growing_crime = None
        max_growth_rate = -np.inf
        
        for crime in self.crime_columns[:-1]: # skip total
            start_val = start_year[crime]
            end_val = end_year[crime]
            
            # To avoid division by zero issues
            if start_val < 5 and end_val < 5: continue
            
            growth_rate = (end_val - start_val) / max(start_val, 1) * 100
            
            if growth_rate > max_growth_rate:
                max_growth_rate = growth_rate
                fastest_growing_crime = crime
                
        if not fastest_growing_crime:
            return [{
                "title": "General Surveillance",
                "description": "Crime rates are relatively stable. Focus on community policing to maintain peace.",
                "urgency": "Low"
            }]
            
        # Recommendation Rules Base
        recommendations = []
        
        if max_growth_rate > 20:
            urgency = "High" 
        elif max_growth_rate > 0:
            urgency = "Medium"
        else:
            urgency = "Low"
            
        if fastest_growing_crime == "Cybercrimes":
            recommendations.append({
                "title": "Cybersecurity Awareness Program",
                "description": f"Cybercrimes have grown by {max_growth_rate:.1f}%. Initiate state-wide digital literacy drives and set up specialized cyber-cells in major districts.",
                "urgency": urgency
            })
        elif fastest_growing_crime == "Theft" or fastest_growing_crime == "Burglary":
            recommendations.append({
                "title": "Urban Patrol Fortification",
                "description": f"Property crimes ({fastest_growing_crime}) rose by {max_growth_rate:.1f}%. Increase nighttime CCTV coverage in vulnerable urban zones and promote neighborhood watch programs.",
                "urgency": urgency
            })
        elif fastest_growing_crime == "Rape":
             recommendations.append({
                "title": "Women Safety & Rapid Response",
                "description": f"Urgent attention required. Implement robust fast-track courts, ensure well-lit transit zones, and launch a 24/7 dedicated distress hotline.",
                "urgency": "Critical"
            })
        else:
            recommendations.append({
                "title": f"Targeted Response for {fastest_growing_crime}",
                "description": f"We detected a {max_growth_rate:.1f}% growth in {fastest_growing_crime}. Reallocate police personnel to investigate the root socio-economic triggers for this spike.",
                "urgency": urgency
            })
            
        return recommendations

# Initialize at startup to keep it in memory
ml_engine = CrimeMLEngine()
