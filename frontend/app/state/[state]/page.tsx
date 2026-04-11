import StateDashboard from "@/components/state-dashboard"
import CrimeGrid from "@/components/crime-grid"

export default async function StatePage({ params }: { params: Promise<{ state: string }> }) {
  // In Next.js 15, params is asynchronous, so we must await it or access unwrapped inside boundary safely if using use client.
  // We'll await it for server components.
  const resolvedParams = await params;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <StateDashboard stateName={resolvedParams.state} />
      <CrimeGrid stateName={resolvedParams.state} />
    </div>
  )
}
