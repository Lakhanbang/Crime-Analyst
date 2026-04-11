"use client"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, AlertTriangle, ShieldCheck, Activity } from "lucide-react"

const stats = [
  {
    title: "Total Cases (2024)",
    value: "3,421,500",
    change: "+2.4%",
    trend: "up",
    icon: Activity,
    color: "text-blue-500"
  },
  {
    title: "Top Risk State",
    value: "Maharashtra",
    change: "High Alert",
    trend: "up",
    icon: AlertTriangle,
    color: "text-red-500"
  },
  {
    title: "Fastest Growing Crime",
    value: "Cyber Fraud",
    change: "+45%",
    trend: "up",
    icon: TrendingUp,
    color: "text-orange-500"
  },
  {
    title: "Forecasted 2030 Total",
    value: "2,850,000",
    change: "-16.7%",
    trend: "down",
    icon: ShieldCheck,
    color: "text-green-500"
  }
]

export default function StatsCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
      {stats.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
          >
            <Card className="hover:border-primary/50 transition-colors group">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-xl bg-white/5 group-hover:bg-white/10 transition-colors ${stat.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${stat.trend === 'up' && stat.change.includes('+') ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                    {stat.change}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-medium mb-1">{stat.title}</p>
                  <h3 className="text-2xl font-bold tracking-tight">{stat.value}</h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )
      })}
    </div>
  )
}
