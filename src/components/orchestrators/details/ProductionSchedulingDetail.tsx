import { useState } from "react";
import { motion } from "framer-motion";
import { Play, Clock, CheckCircle2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const machines = [
  { id: "M1", name: "Injection Molder A", capacity: 92, currentJob: "Widget A – Batch 047", eta: "2h 15m", status: "running" },
  { id: "M2", name: "Extrusion Line B", capacity: 87, currentJob: "Widget C – Batch 023", eta: "4h 30m", status: "running" },
  { id: "M3", name: "CNC Router C", capacity: 95, currentJob: "Widget B – Batch 031", eta: "1h 45m", status: "running" },
  { id: "M4", name: "Assembly Unit D", capacity: 78, currentJob: "Maintenance", eta: "—", status: "maintenance" },
  { id: "M5", name: "Packaging Line E", capacity: 88, currentJob: "Widget A – Batch 046", eta: "3h 10m", status: "running" },
];

const schedule = [
  { time: "06:00", m1: "Widget A", m2: "Widget C", m3: "Widget B", m4: "—", m5: "Widget A" },
  { time: "10:00", m1: "Widget B", m2: "Widget A", m3: "Widget C", m4: "Maint.", m5: "Widget B" },
  { time: "14:00", m1: "Widget C", m2: "Widget B", m3: "Widget A", m4: "Widget D", m5: "Widget C" },
  { time: "18:00", m1: "Widget A", m2: "Widget D", m3: "Widget B", m4: "Widget A", m5: "Widget D" },
  { time: "22:00", m1: "—", m2: "Widget C", m3: "—", m4: "Widget B", m5: "—" },
];

export function ProductionSchedulingDetail() {
  const [optimizing, setOptimizing] = useState(false);
  const [optimized, setOptimized] = useState(false);

  const handleOptimize = () => {
    setOptimizing(true);
    setTimeout(() => { setOptimizing(false); setOptimized(true); }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Machine Status */}
      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Live Machine Status</h4>
        <div className="space-y-3">
          {machines.map((m, i) => (
            <motion.div key={m.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-4 p-3 rounded-xl bg-muted/50">
              <div className="flex items-center gap-2 w-40">
                <span className={`w-2 h-2 rounded-full ${m.status === "running" ? "bg-[hsl(142,71%,45%)] animate-pulse" : "bg-[hsl(38,92%,50%)]"}`} />
                <span className="text-sm font-medium">{m.id}</span>
                <span className="text-xs text-muted-foreground hidden md:inline">{m.name}</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-muted-foreground">{m.currentJob}</span>
                  <span className="text-xs font-medium">{m.capacity}%</span>
                </div>
                <Progress value={m.capacity} className="h-1.5" />
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground w-20 justify-end">
                <Clock className="w-3 h-3" />
                {m.eta}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Schedule Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Today's Schedule</h4>
          <Button size="sm" onClick={handleOptimize} disabled={optimizing || optimized} className="h-8 text-xs rounded-lg">
            {optimizing ? <><Clock className="w-3 h-3 mr-1 animate-spin" /> Optimizing…</> : optimized ? <><CheckCircle2 className="w-3 h-3 mr-1" /> Optimized</> : <><Play className="w-3 h-3 mr-1" /> Re-Optimize</>}
          </Button>
        </div>
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-muted/50">
                <th className="text-left p-2.5 font-medium text-muted-foreground">Time</th>
                {["M1", "M2", "M3", "M4", "M5"].map(m => <th key={m} className="text-left p-2.5 font-medium text-muted-foreground">{m}</th>)}
              </tr>
            </thead>
            <tbody>
              {schedule.map((row, i) => (
                <motion.tr key={row.time} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 + i * 0.05 }} className="border-t border-border">
                  <td className="p-2.5 font-medium">{row.time}</td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${row.m1 === "—" ? "bg-muted text-muted-foreground" : optimized ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : "bg-foreground/5"}`}>{row.m1}</span></td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${row.m2 === "—" ? "bg-muted text-muted-foreground" : "bg-foreground/5"}`}>{row.m2}</span></td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${row.m3 === "—" ? "bg-muted text-muted-foreground" : "bg-foreground/5"}`}>{row.m3}</span></td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${row.m4 === "Maint." ? "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]" : row.m4 === "—" ? "bg-muted text-muted-foreground" : "bg-foreground/5"}`}>{row.m4}</span></td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${row.m5 === "—" ? "bg-muted text-muted-foreground" : "bg-foreground/5"}`}>{row.m5}</span></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Overall Utilization", value: "94%", sub: "+3% from last week" },
          { label: "Orders Scheduled", value: "23", sub: "5 pending allocation" },
          { label: "Changeover Time", value: "12min", sub: "Reduced by 18%" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + i * 0.1 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className="text-lg font-semibold">{s.value}</p>
            <p className="text-[10px] font-medium text-muted-foreground">{s.label}</p>
            <p className="text-[10px] text-[hsl(142,71%,45%)] mt-0.5">{s.sub}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
