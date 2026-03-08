import { motion } from "framer-motion";
import { Zap, ArrowRight } from "lucide-react";

const recommendations = [
  { product: "Widget B", confidence: 94, reason: "High demand trend, low changeover from current setup", efficiency: "+15%", changeover: "12 min", demand: "↑ 23%" },
  { product: "Widget D", confidence: 87, reason: "Premium margin product, slot available on M3", efficiency: "+8%", changeover: "28 min", demand: "↑ 12%" },
  { product: "Widget A", confidence: 82, reason: "Steady demand, existing raw material in stock", efficiency: "+5%", changeover: "8 min", demand: "→ Stable" },
];

export function ProductionRecommendationDetail() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 p-3 rounded-xl bg-muted/50">
        <Zap className="w-4 h-4 text-[hsl(142,71%,45%)]" />
        <p className="text-xs text-muted-foreground">Based on 6 months of production data, demand patterns, and machine availability</p>
      </div>

      <div className="space-y-3">
        {recommendations.map((r, i) => (
          <motion.div key={r.product} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className={`p-5 rounded-xl border ${i === 0 ? "border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)]" : "border-border"} hover:border-foreground/20 transition-colors`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className={`text-xs font-bold px-2.5 py-1 rounded-lg ${i === 0 ? "bg-foreground text-background" : "bg-muted"}`}>#{i + 1}</span>
                <div>
                  <p className="text-sm font-semibold">{r.product}</p>
                  <p className="text-[10px] text-muted-foreground">{r.reason}</p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs font-semibold text-[hsl(142,71%,45%)]">
                {r.confidence}% match
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="p-2 rounded-lg bg-muted/50"><p className="text-[10px] text-muted-foreground">Efficiency Gain</p><p className="text-sm font-medium text-[hsl(142,71%,45%)]">{r.efficiency}</p></div>
              <div className="p-2 rounded-lg bg-muted/50"><p className="text-[10px] text-muted-foreground">Changeover</p><p className="text-sm font-medium">{r.changeover}</p></div>
              <div className="p-2 rounded-lg bg-muted/50"><p className="text-[10px] text-muted-foreground">Demand</p><p className="text-sm font-medium">{r.demand}</p></div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
