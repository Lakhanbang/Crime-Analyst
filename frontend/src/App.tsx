import { useState, useEffect } from 'react';
import { ShieldAlert, TrendingUp, Map as MapIcon, Activity } from 'lucide-react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip as ChartTooltip, Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';
import './index.css';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, ChartTooltip, Legend
);

// Use current host for production on Vercel, or localhost for local dev
const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api';

function App() {
  const [selectedState, setSelectedState] = useState<string>('');
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [forecastData, setForecastData] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const crimeTypes = [
    'Total Crimes', 'Cybercrimes', 'Rape', 'Theft', 'Murders', 
    'Kidnapping & Abduction', 'Burglary'
  ];
  const [selectedCrime, setSelectedCrime] = useState('Total Crimes');

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/states`).then(res => res.json()),
      fetch(`${API_BASE}/clustering`).then(res => res.json())
    ]).then(([statesData, clustersData]) => {
      setClusters(clustersData.clusters || []);
      if (statesData.states && statesData.states.length > 0) {
        setSelectedState(statesData.states[0]);
      } else {
        setLoading(false);
      }
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (!selectedState) return;
    
    setLoading(true);
    fetch(`${API_BASE}/historical/${encodeURIComponent(selectedState)}`)
      .then(res => res.json())
      .then(history => {
        setHistoricalData(history.data || []);
        return fetch(`${API_BASE}/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ state_name: selectedState, target_crime: selectedCrime, years_ahead: 5 })
        });
      })
      .then(res => res.json())
      .then(forecast => {
        setForecastData(forecast.forecast || []);
        return fetch(`${API_BASE}/insights/${encodeURIComponent(selectedState)}`);
      })
      .then(res => res.json())
      .then(insightsData => {
        setInsights(insightsData.recommendations || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [selectedState, selectedCrime]);

  const combinedData = [...historicalData, ...forecastData];
  const stateCluster = clusters.find(c => c.State === selectedState);

  const chartData = {
    labels: combinedData.map(d => d.Year),
    datasets: [
      {
        label: 'Historical Crime',
        data: combinedData.map(d => d.is_prediction ? null : d[selectedCrime]),
        borderColor: 'rgba(14, 165, 233, 1)',
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        tension: 0.3,
        pointRadius: 4,
      },
      {
        label: 'AI Projection',
        data: combinedData.map((d, index) => {
           if (d.is_prediction) return d[selectedCrime];
           if (index === historicalData.length - 1) return d[selectedCrime];
           return null;
        }),
        borderColor: 'rgba(139, 92, 246, 1)',
        backgroundColor: 'rgba(139, 92, 246, 0.5)',
        borderDash: [5, 5],
        tension: 0.3,
        pointRadius: 4,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#0f172a',
          font: { family: 'Outfit' }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255,255,255,0.9)',
        titleColor: '#0f172a',
        bodyColor: '#475569',
        borderColor: 'rgba(14, 165, 233, 0.2)',
        borderWidth: 1,
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(15,23,42,0.05)' },
        ticks: { color: '#475569' }
      },
      y: {
        grid: { color: 'rgba(15,23,42,0.05)' },
        ticks: { color: '#475569' }
      }
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch(riskLevel) {
      case 'High Risk': return '#f43f5e';
      case 'Medium Risk': return '#f59e0b';
      case 'Low Risk': return '#10b981';
      default: return '#cbd5e1';
    }
  };

  const mapCenter: [number, number] = [80, 22];

  return (
    <div className="app-container" style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem', display: 'flex', alignItems: 'center', gap: '12px', fontWeight: '700' }}>
            <Activity size={36} color="var(--accent-cyan)" />
            Crime Analyst
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            Predictive modeling and automated policy responses
          </p>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        
        {/* Left Column: Map & Chart */}
        <div style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '450px' }}>
            <h2 style={{ marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <MapIcon color="var(--accent-amber)" />
              India Crime Map (Risk Assessment)
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '10px' }}>Click on a state to view targeted analytics and insights</p>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ComposableMap
                projection="geoMercator"
                projectionConfig={{ scale: 800, center: mapCenter }}
                style={{ width: '100%', height: '100%' }}
              >
                <Geographies geography="/states_india.geojson">
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      const stateName = geo.properties.st_nm;
                      const clusterInfo = clusters.find(c => c.State === stateName);
                      const isSelected = selectedState === stateName;
                      
                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          onClick={() => setSelectedState(stateName)}
                          data-tooltip-id="map-tooltip"
                          data-tooltip-content={`${stateName} - ${clusterInfo?.RiskLevel || 'No Data'}`}
                          style={{
                            default: {
                              fill: isSelected ? 'rgba(14, 165, 233, 0.4)' : (clusterInfo ? getRiskColor(clusterInfo.RiskLevel) : '#cbd5e1'),
                              stroke: '#ffffff',
                              strokeWidth: isSelected ? 2 : 0.5,
                              outline: 'none',
                              opacity: isSelected ? 1 : 0.8
                            },
                            hover: {
                              fill: 'rgba(14, 165, 233, 0.6)',
                              stroke: '#ffffff',
                              strokeWidth: 2,
                              outline: 'none',
                              cursor: 'pointer'
                            },
                            pressed: {
                              fill: 'var(--accent-cyan)',
                              outline: 'none',
                            }
                          }}
                        />
                      );
                    })
                  }
                </Geographies>
              </ComposableMap>
              <Tooltip id="map-tooltip" />
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', height: '400px' }}>
            <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <TrendingUp color="var(--accent-purple)" />
              {selectedCrime} Forecast in {selectedState} (2013 - 2027)
            </h2>
            {loading && historicalData.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
                <div className="loader"></div>
              </div>
            ) : (
              <div style={{ height: '300px' }}>
                 <Line data={chartData} options={chartOptions} />
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Controls & Insights */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Activity color="var(--accent-cyan)" />
              Crime Categories
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', fontSize: '0.9rem' }}>
              Select a crime category to forecast
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {crimeTypes.map(c => (
                <label key={c} className="crime-label">
                  <input 
                    type="checkbox" 
                    className="crime-checkbox" 
                    checked={selectedCrime === c} 
                    onChange={() => setSelectedCrime(c)} 
                  />
                  <span style={{ color: selectedCrime === c ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{c}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <MapIcon color="var(--accent-green)" />
              Selected State Profile
            </h2>
            <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Region: </span> 
              <span style={{ fontWeight: '600' }}>{selectedState || 'None'}</span>
            </div>
            <div style={{ fontSize: '1.2rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Risk Assessment: </span> 
              <span style={{ 
                color: stateCluster ? getRiskColor(stateCluster.RiskLevel) : 'var(--text-secondary)',
                fontWeight: 'bold'
              }}>
                {stateCluster?.RiskLevel || 'Calculating...'}
              </span>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', flex: 1, overflowY: 'auto', maxHeight: '500px' }}>
            <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--accent-red)' }}>
              <ShieldAlert />
              AI Policy Recommendations
            </h2>
            {loading ? (
              <div className="loader" style={{ margin: '0 auto' }}></div>
            ) : insights.length > 0 ? (
              insights.map((insight, idx) => (
                <div key={idx} style={{ 
                  background: 'rgba(15, 23, 42, 0.03)', 
                  padding: '16px', 
                  borderRadius: '12px',
                  borderLeft: `4px solid ${insight.urgency === 'Critical' ? 'var(--accent-red)' : 'var(--accent-cyan)'}`,
                  marginBottom: '16px'
                }}>
                  <h3 style={{ marginBottom: '8px', fontSize: '1.1rem' }}>{insight.title}</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                    {insight.description}
                  </p>
                  <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Urgency: <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{insight.urgency}</span>
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-secondary)' }}>No recommendations available.</p>
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
}

export default App;
