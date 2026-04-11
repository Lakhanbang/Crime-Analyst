import Link from "next/link";
import { Shield } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-background/40 py-8 md:py-12 mt-20">
      <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-2 text-foreground/80">
          <Shield className="w-5 h-5" />
          <span className="font-semibold tracking-tight text-lg">CrimeMetrics AI</span>
        </div>
        <p className="text-sm text-muted-foreground text-center md:text-left">
          &copy; {new Date().getFullYear()} Crime Analytics Platform. AI Forecasting till 2030.
        </p>
        <div className="flex gap-4 text-sm font-medium text-muted-foreground">
          <Link href="/about" className="hover:text-primary transition-colors">Data Sources</Link>
          <Link href="/about" className="hover:text-primary transition-colors">Privacy</Link>
        </div>
      </div>
    </footer>
  );
}
