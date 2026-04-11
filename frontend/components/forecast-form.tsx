"use client"
import { useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowRight } from "lucide-react"
import ChartCard from "@/components/chart-card"

export default function ForecastForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<null | any>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setResult({
        predicted: 4250,
        confidence: 88,
        data: [
          { year: "2024", cases: 2200 },
          { year: "2025", cases: 2500 },
          { year: "2026", cases: 2900 },
          { year: "2027", cases: 3300 },
          { year: "2028", cases: 3750 },
          { year: "2029", cases: 4000 },
          { year: "2030", cases: 4250 },
        ]
      })
      setLoading(false)
    }, 1500)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle>Forecast Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">State</label>
              <select className="w-full h-10 px-3 rounded-md border border-input bg-background/50 focus:ring-2 focus:ring-primary">
                <option>Maharashtra</option>
                <option>Delhi</option>
                <option>Karnataka</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Crime Type</label>
              <select className="w-full h-10 px-3 rounded-md border border-input bg-background/50 focus:ring-2 focus:ring-primary">
                <option>Cybercrime</option>
                <option>Theft</option>
                <option>Fraud</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Target Year</label>
              <select className="w-full h-10 px-3 rounded-md border border-input bg-background/50 focus:ring-2 focus:ring-primary">
                <option>2030</option>
                <option>2028</option>
                <option>2026</option>
              </select>
            </div>
            <Button type="submit" className="w-full mt-4" disabled={loading}>
              {loading ? <Loader2 className="mr-2 animate-spin" /> : <p className="flex items-center">Generate AI Forecast <ArrowRight className="w-4 h-4 ml-2"/></p>}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="lg:col-span-2">
        {result ? (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <Card className="bg-primary/10 border-primary/20">
                <CardContent className="p-6">
                  <p className="text-sm text-primary mb-1 font-medium">Predicted Cases</p>
                  <p className="text-4xl font-bold">{result.predicted}</p>
                </CardContent>
              </Card>
              <Card className="bg-green-500/10 border-green-500/20">
                <CardContent className="p-6">
                  <p className="text-sm text-green-500 mb-1 font-medium">AI Confidence Score</p>
                  <p className="text-4xl font-bold text-green-500">{result.confidence}%</p>
                </CardContent>
              </Card>
            </div>
            <ChartCard title="Future Projection" data={result.data} dataKey="cases" colorStr="hsl(var(--primary))" />
          </motion.div>
        ) : (
          <div className="h-full min-h-[400px] flex items-center justify-center border border-dashed border-border rounded-xl bg-background/30 max-h-min">
            <p className="text-muted-foreground text-center max-w-sm">Select parameters and generate a forecast to visualize AI-driven predictions.</p>
          </div>
        )}
      </div>
    </div>
  )
}
