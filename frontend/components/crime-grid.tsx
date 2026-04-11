"use client"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { ArrowRight, FileText, MonitorDot, AlertCircle, ShieldBan, UserX, Home } from "lucide-react"
import Link from "next/link"

const crimeTypes = [
  { id: "murder", name: "Murder", icon: UserX, color: "text-red-500", cases: "4,230 YTD" },
  { id: "theft", name: "Theft", icon: Home, color: "text-orange-500", cases: "28,100 YTD" },
  { id: "cybercrime", name: "Cybercrime", icon: MonitorDot, color: "text-blue-500", cases: "45,900 YTD" },
  { id: "fraud", name: "Fraud", icon: FileText, color: "text-yellow-500", cases: "12,450 YTD" },
  { id: "assault", name: "Assault", icon: AlertCircle, color: "text-pink-500", cases: "19,800 YTD" },
  { id: "burglary", name: "Burglary", icon: ShieldBan, color: "text-purple-500", cases: "15,200 YTD" },
]

export default function CrimeGrid({ stateName }: { stateName: string }) {
  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold tracking-tight mb-6">Crime Categories</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {crimeTypes.map((crime, i) => {
          const Icon = crime.icon
          return (
            <motion.div key={crime.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
              <Link href={`/state/${stateName}/crime/${crime.id}`}>
                <Card className="hover:border-primary/50 transition-all hover:shadow-lg cursor-pointer group bg-gradient-to-br from-white/5 to-transparent hover:from-white/10 hover:to-transparent">
                  <CardContent className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-xl bg-white/5 group-hover:bg-white/10 transition-colors ${crime.color}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">{crime.name}</h3>
                        <p className="text-sm text-muted-foreground">{crime.cases}</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
