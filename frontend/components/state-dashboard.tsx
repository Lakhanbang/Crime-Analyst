"use client"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell, BarChart, Bar } from "recharts"
import { Activity, ShieldAlert, ArrowUpRight, Target } from "lucide-react"

const yearlyData = [
  { year: "2018", incidents: 420 },
  { year: "2019", incidents: 450 },
  { year: "2020", incidents: 510 },
  { year: "2021", incidents: 480 },
  { year: "2022", incidents: 460 },
  { year: "2023", incidents: 440 },
  { year: "2024", incidents: 435 },
]

const crimeSplitData = [
  { name: "Theft", value: 400 },
  { name: "Assault", value: 300 },
  { name: "Cybercrime", value: 300 },
  { name: "Fraud", value: 200 },
]

const COLORS = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))']

const arrestData = [
  { month: "Jan", arrests: 65, crimes: 80 },
  { month: "Feb", arrests: 59, crimes: 75 },
  { month: "Mar", arrests: 80, crimes: 90 },
  { month: "Apr", arrests: 81, crimes: 85 },
  { month: "May", arrests: 56, crimes: 70 },
]

export default function StateDashboard({ stateName }: { stateName: string }) {
  const formattedState = stateName.replace("-", " ").toUpperCase()

  return (
    <div className="w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <h1 className="text-4xl font-extrabold tracking-tight">{formattedState} Analytics</h1>
          <p className="text-muted-foreground mt-1">Real-time statistics and 2030 projections.</p>
        </motion.div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { title: "Total Crimes (YTD)", value: "142,504", icon: Activity, color: "text-blue-500", detail: "+4.1% vs last year" },
          { title: "Total Arrests", value: "98,230", icon: Target, color: "text-green-500", detail: "68.9% resolution rate" },
          { title: "Risk Score", value: "85/100", icon: ShieldAlert, color: "text-red-500", detail: "Critical condition" },
          { title: "2030 Projected Score", value: "72/100", icon: ArrowUpRight, color: "text-orange-500", detail: "Decreasing trend" }
        ].map((kpi, i) => {
          const Icon = kpi.icon
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card className="hover:border-primary/50 transition-colors">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className={`p-3 rounded-xl bg-white/5 ${kpi.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground font-medium mb-1">{kpi.title}</p>
                  <h3 className="text-2xl font-bold tracking-tight mb-2">{kpi.value}</h3>
                  <p className="text-xs text-muted-foreground">{kpi.detail}</p>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Yearly Crime Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={yearlyData}>
                <defs>
                  <linearGradient id="colorInc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="year" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }} />
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                <Area type="monotone" dataKey="incidents" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorInc)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Crime Split</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={crimeSplitData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {crimeSplitData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
