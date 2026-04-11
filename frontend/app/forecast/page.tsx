import ForecastForm from "@/components/forecast-form"

export default function ForecastPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <div className="mb-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">AI Crime Forecasting</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Utilize our advanced neural networks to predict future crime trends across Indian states up to the year 2030.
        </p>
      </div>
      <ForecastForm />
    </div>
  )
}
