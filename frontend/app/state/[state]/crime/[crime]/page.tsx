import ChartCard from "@/components/chart-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ShieldAlert, TrendingUp, Cpu, Activity } from "lucide-react"

export default async function CrimePage({ params }: { params: Promise<{ state: string, crime: string }> }) {
  const resolvedParams = await params;
  const stateFormatted = resolvedParams.state.replace("-", " ").toUpperCase();
  const crimeFormatted = resolvedParams.crime.replace("-", " ").toUpperCase();

  const mockData = [
    { year: "2020", incidents: 1200 },
    { year: "2021", incidents: 1500 },
    { year: "2022", incidents: 1800 },
    { year: "2023", incidents: 2400 },
    { year: "2024", incidents: 2200 },
    { year: "2025", incidents: 2500 },
    { year: "2026", incidents: 2750 },
    { year: "2030", incidents: 3400 },
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight text-primary">
          {crimeFormatted} <span className="text-foreground">in {stateFormatted}</span>
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">Detailed analysis and AI-driven predictive modeling.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2"><Activity className="w-4 h-4"/> Current Standard</h3>
            <p className="text-3xl font-bold">2,200 <span className="text-sm text-red-500 font-normal">in 2024</span></p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2"><TrendingUp className="w-4 h-4"/> Growth %</h3>
            <p className="text-3xl font-bold">+18.4% <span className="text-sm text-muted-foreground font-normal">vs average</span></p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2"><ShieldAlert className="w-4 h-4"/> India Average</h3>
            <p className="text-3xl font-bold">1,850</p>
          </CardContent>
        </Card>
        <Card className="bg-blue-500/5 border-blue-500/20">
          <CardContent className="p-6">
            <h3 className="text-sm font-medium text-blue-500/80 mb-2 flex items-center gap-2"><Cpu className="w-4 h-4"/> Forecast 2030</h3>
            <p className="text-3xl font-bold text-blue-500">3,400</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <ChartCard 
            title={`${crimeFormatted} Trend & Forecast to 2030`} 
            data={mockData} 
            dataKey="incidents" 
            colorStr="hsl(var(--primary))" 
          />
        </div>
        
        <Card className="h-full bg-gradient-to-b from-primary/10 to-transparent border-primary/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Cpu className="w-32 h-32" />
          </div>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="text-primary w-5 h-5" /> 
              AI Insights
            </CardTitle>
          </CardHeader>
          <CardContent className="relative z-10 prose dark:prose-invert">
            <p className="text-muted-foreground">
              Based on the time-series analysis and our predictive modeling, <strong>{crimeFormatted}</strong> in <strong>{stateFormatted}</strong> is showing a rapid upward trajectory.
            </p>
            <ul className="text-sm mt-4 space-y-2">
              <li>High correlation with urban expansion.</li>
              <li>Expected peak around 2027 if current arrest rates persist.</li>
              <li>Slight dip in 2024 potentially due to recent policy interventions.</li>
            </ul>
            <div className="mt-6 p-4 bg-background/50 rounded-xl border border-white/10">
              <strong>Recommendation:</strong> Increase digital patrol units by 15% in major demographic hubs.
            </div>
          </CardContent>
        </Card>
      </div>

    </div>
  )
}
