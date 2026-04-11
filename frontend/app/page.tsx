import Hero from "@/components/hero";
import StatsCards from "@/components/stats-cards";
import NationalCharts from "@/components/national-charts";
import IndiaMap from "@/components/india-map";

export default function Home() {
  return (
    <div className="w-full">
      <Hero />
      <div className="container mx-auto px-4" id="map-section">
        <StatsCards />
        
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-12 items-center mb-24">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-4">Interactive Analytics map</h2>
            <p className="text-muted-foreground mb-8">
              Select a state to deep dive into its crime statistics, risk indices, and AI-driven forecasts. Our platform provides real-time geospatial intelligence.
            </p>
            <IndiaMap />
          </div>
          <div>
            <NationalCharts />
          </div>
        </div>
      </div>
    </div>
  );
}
