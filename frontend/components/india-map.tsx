"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useRouter } from "next/navigation"

// Sleek Abstract Hexagon/Diamond Grid representation of states
const mockStates = [
  { id: "delhi", name: "Delhi", x: 40, y: 20, intensity: 80, cases: "320k" },
  { id: "uttar-pradesh", name: "Uttar Pradesh", x: 60, y: 35, intensity: 95, cases: "650k" },
  { id: "rajasthan", name: "Rajasthan", x: 25, y: 40, intensity: 50, cases: "210k" },
  { id: "gujarat", name: "Gujarat", x: 15, y: 55, intensity: 40, cases: "180k" },
  { id: "madhya-pradesh", name: "Madhya Pradesh", x: 45, y: 50, intensity: 70, cases: "440k" },
  { id: "maharashtra", name: "Maharashtra", x: 30, y: 70, intensity: 85, cases: "580k" },
  { id: "karnataka", name: "Karnataka", x: 40, y: 85, intensity: 60, cases: "290k" },
  { id: "tamil-nadu", name: "Tamil Nadu", x: 50, y: 95, intensity: 55, cases: "310k" },
  { id: "west-bengal", name: "West Bengal", x: 80, y: 50, intensity: 75, cases: "410k" },
]

export default function IndiaMap() {
  const [hovered, setHovered] = useState<string | null>(null)
  const router = useRouter()

  return (
    <div className="relative w-full aspect-square max-w-2xl mx-auto drop-shadow-2xl mb-12">
      <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-primary/5 rounded-full blur-3xl -z-10" />
      
      {/* Grid background lines for SaaS feel */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)]"></div>

      <div className="relative w-full h-full p-8">
        {mockStates.map((state) => (
          <motion.div
            key={state.id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            whileHover={{ scale: 1.2, zIndex: 10 }}
            onHoverStart={() => setHovered(state.id)}
            onHoverEnd={() => setHovered(null)}
            onClick={() => router.push(`/state/${state.id}`)}
            className="absolute cursor-pointer flex flex-col items-center justify-center transition-all duration-300"
            style={{ left: `${state.x}%`, top: `${state.y}%` }}
          >
            {/* Pulsing indicator */}
            <div className="relative flex h-8 w-8 items-center justify-center">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-40`}
                    style={{ backgroundColor: `hsl(var(--primary))` }}></span>
              <span className={`relative inline-flex rounded-full h-4 w-4 shadow-lg border border-white/20`}
                    style={{ backgroundColor: `hsl(var(--primary))`}}></span>
            </div>

            {/* Custom Tooltip */}
            <AnimatePresence>
              {hovered === state.id && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 5, scale: 0.9 }}
                  className="absolute bottom-10 whitespace-nowrap bg-background/80 backdrop-blur-xl border border-white/10 px-4 py-2 rounded-xl shadow-2xl z-50 pointer-events-none"
                >
                  <p className="font-bold text-sm text-foreground">{state.name}</p>
                  <p className="text-xs text-muted-foreground">{state.cases} Cases</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
