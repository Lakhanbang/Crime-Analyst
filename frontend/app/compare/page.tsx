"use client"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts"

const radarData = [
  { subject: "Violent", A: 120, B: 110, fullMark: 150 },
  { subject: "Property", A: 98, B: 130, fullMark: 150 },
  { subject: "Cyber", A: 86, B: 130, fullMark: 150 },
  { subject: "Economic", A: 99, B: 100, fullMark: 150 },
  { subject: "Organized", A: 85, B: 90, fullMark: 150 },
  { subject: "Other", A: 65, B: 85, fullMark: 150 },
]

const growthData = [
  { year: "2020", "State A": 4000, "State B": 2400 },
  { year: "2021", "State A": 3000, "State B": 1398 },
  { year: "2022", "State A": 2000, "State B": 9800 },
  { year: "2023", "State A": 2780, "State B": 3908 },
  { year: "2024", "State A": 1890, "State B": 4800 },
]

export default function ComparePage() {
  const [stateA, setStateA] = useState("Maharashtra")
  const [stateB, setStateB] = useState("Delhi")

  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <h1 className="text-4xl font-extrabold tracking-tight mb-8">State Comparison</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <select value={stateA} onChange={(e) => setStateA(e.target.value)} className="w-full h-12 px-4 rounded-xl border border-input bg-background/50 focus:ring-2 focus:ring-primary font-semibold text-lg">
          <option>Maharashtra</option>
          <option>Uttar Pradesh</option>
          <option>Karnataka</option>
        </select>
        <select value={stateB} onChange={(e) => setStateB(e.target.value)} className="w-full h-12 px-4 rounded-xl border border-input bg-background/50 focus:ring-2 focus:ring-blue-500 font-semibold text-lg">
          <option>Delhi</option>
          <option>Rajasthan</option>
          <option>Gujarat</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <Card className="border-primary/50">
          <CardContent className="p-6 text-center">
            <h3 className="text-xl font-bold mb-2">{stateA} Total (YTD)</h3>
            <p className="text-4xl font-extrabold text-primary">580,240</p>
          </CardContent>
        </Card>
        <Card className="border-blue-500/50">
          <CardContent className="p-6 text-center">
            <h3 className="text-xl font-bold mb-2">{stateB} Total (YTD)</h3>
            <p className="text-4xl font-extrabold text-blue-500">320,110</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Crime Profile Radar</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="hsl(var(--border))" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                <Radar name={stateA} dataKey="A" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.6} />
                <Radar name={stateB} dataKey="B" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Legend />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Yearly Growth Comparison</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={growthData}>
                <XAxis dataKey="year" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="State A" name={stateA} fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="State B" name={stateB} fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
