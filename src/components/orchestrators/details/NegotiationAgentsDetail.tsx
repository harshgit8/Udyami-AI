import { motion } from "framer-motion";
import { Handshake, CheckCircle2, Clock } from "lucide-react";

const negotiations = [
  { supplier: "PolyChem India", material: "ABS Resin", initial: 195, final: 168, savings: "14%", status: "completed", rounds: 4 },
  { supplier: "Apex Materials", material: "PA66 Pellets", initial: 320, final: 285, savings: "11%", status: "completed", rounds: 3 },
  { supplier: "GreenPoly Ltd", material: "PP Compound", initial: 142, final: null, savings: null, status: "in_progress", rounds: 2 },
  { supplier: "TechMat Corp", material: "PC Granules", initial: 280, final: 248, savings: "11.4%", status: "completed", rounds: 5 },
];

export function NegotiationAgentsDetail() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Negotiations Done", value: "3/4", sub: "This week" },
          { label: "Avg Savings", value: "12.1%", sub: "vs initial quotes" },
          { label: "Total Saved", value: "₹1.8L", sub: "This month" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className="text-lg font-semibold">{s.value}</p>
            <p className="text-[10px] text-muted-foreground">{s.label}</p>
            <p className="text-[10px] text-[hsl(142,71%,45%)]">{s.sub}</p>
          </motion.div>
        ))}
      </div>

      <div className="space-y-3">
        {negotiations.map((n, i) => (
          <motion.div key={n.supplier} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }} className="p-4 rounded-xl border border-border hover:border-foreground/20 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {n.status === "completed" ? <CheckCircle2 className="w-3.5 h-3.5 text-[hsl(142,71%,45%)]" /> : <Clock className="w-3.5 h-3.5 text-[hsl(38,92%,50%)] animate-pulse" />}
                <span className="text-sm font-medium">{n.supplier}</span>
              </div>
              <span className="text-[10px] text-muted-foreground">{n.rounds} rounds</span>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
              <div><p className="text-[10px] text-muted-foreground">Material</p><p className="text-xs font-medium">{n.material}</p></div>
              <div><p className="text-[10px] text-muted-foreground">Initial</p><p className="text-xs font-medium">₹{n.initial}/kg</p></div>
              <div><p className="text-[10px] text-muted-foreground">Final</p><p className="text-xs font-medium">{n.final ? `₹${n.final}/kg` : "—"}</p></div>
              <div><p className="text-[10px] text-muted-foreground">Savings</p><p className="text-xs font-medium text-[hsl(142,71%,45%)]">{n.savings || "Pending"}</p></div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
