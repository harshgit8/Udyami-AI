import { motion } from "framer-motion";
import { Heart, AlertTriangle, Shield } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const workers = [
  { name: "Rajesh K.", shift: "Morning", fatigue: 22, risk: "low", hours: 7.5 },
  { name: "Priya M.", shift: "Morning", fatigue: 45, risk: "medium", hours: 9.0 },
  { name: "Amit S.", shift: "Night", fatigue: 68, risk: "high", hours: 10.5 },
  { name: "Sunita R.", shift: "Evening", fatigue: 15, risk: "low", hours: 6.0 },
  { name: "Vikram P.", shift: "Night", fatigue: 55, risk: "medium", hours: 8.5 },
];

export function WorkforceWellbeingDetail() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Overall Risk", value: "Low", color: "text-[hsl(142,71%,45%)]" },
          { label: "Active Workers", value: "24", color: "text-foreground" },
          { label: "Avg Fatigue", value: "32%", color: "text-foreground" },
          { label: "Safety Score", value: "94/100", color: "text-[hsl(142,71%,45%)]" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className={`text-lg font-semibold ${s.color}`}>{s.value}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Worker Fatigue Monitor</h4>
        <div className="space-y-2">
          {workers.map((w, i) => (
            <motion.div key={w.name} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.06 }} className="flex items-center gap-4 p-3 rounded-xl border border-border hover:bg-muted/30 transition-colors">
              <div className="w-32">
                <p className="text-xs font-medium">{w.name}</p>
                <p className="text-[10px] text-muted-foreground">{w.shift} · {w.hours}h</p>
              </div>
              <div className="flex-1">
                <div className="flex justify-between mb-1">
                  <span className="text-[10px] text-muted-foreground">Fatigue Level</span>
                  <span className="text-[10px] font-medium">{w.fatigue}%</span>
                </div>
                <Progress value={w.fatigue} className="h-1.5" />
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${w.risk === "low" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : w.risk === "high" ? "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>{w.risk}</span>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="p-4 rounded-xl border border-border flex items-start gap-3">
        <Shield className="w-4 h-4 text-[hsl(142,71%,45%)] mt-0.5" />
        <div>
          <h4 className="text-xs font-medium mb-1">Shift Optimization Suggestion</h4>
          <p className="text-xs text-muted-foreground">Amit S. has been on night shift for 5 consecutive days. Recommend rotating to morning shift. Priya M. approaching fatigue threshold — suggest 30-min break.</p>
        </div>
      </div>
    </div>
  );
}
