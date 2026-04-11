import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, Database, Cpu, Layers } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-8 text-center">About The Platform</h1>
      
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Shield className="text-primary"/> Project Purpose</CardTitle>
          </CardHeader>
          <CardContent className="prose dark:prose-invert">
            <p>
              The AI Crime Analytics Platform is built to empower law enforcement and researchers with data-driven insights. 
              By analyzing historical crime data across Indian states, the platform identifies emerging patterns, tracks risk indices, 
              and forecasts future spatial and temporal crime distributions up to 2030.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Database className="text-blue-500"/> Dataset & Sources</CardTitle>
          </CardHeader>
          <CardContent className="prose dark:prose-invert">
            <p>
              Our dataset originates from public records (NCRB) supplemented with socio-economic indicators. 
              We process over 5+ million records covering 36 states and UTs, tracking 20+ crime variants ensuring 
              temporal consistency since 2010.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Cpu className="text-green-500"/> AI Models</CardTitle>
          </CardHeader>
          <CardContent className="prose dark:prose-invert">
            <ul>
              <li><strong>Temporal Forecasting:</strong> Utilizes advanced LSTM and Prophet models for time-series predictions.</li>
              <li><strong>Risk Scoring:</strong> Random Forest classifiers evaluating socio-economic, arrest rate, and demographic variables.</li>
              <li><strong>Anomaly Detection:</strong> Isolation Forests to detect sudden spikes in specific crime categories.</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Layers className="text-purple-500"/> Technology Stack</CardTitle>
          </CardHeader>
          <CardContent className="prose dark:prose-invert">
            <p>
              Built for performance and scalability, our frontend leverages <strong>Next.js 15 (App Router)</strong>, fully typed with <strong>TypeScript</strong>. 
              The sleek, dark-mode native UI is crafted with <strong>Tailwind CSS</strong> and <strong>shadcn/ui</strong>. 
              Fluid micro-interactions and smooth page transitions are powered by <strong>Framer Motion</strong>, while 
              complex data visualizations use <strong>Recharts</strong>.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
