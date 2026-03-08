import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const defectData = [
  { name: "Pass", value: 157, color: "hsl(142, 71%, 45%)" },
  { name: "Minor", value: 28, color: "hsl(0, 0%, 70%)" },
  { name: "Major", value: 12, color: "hsl(38, 92%, 50%)" },
  { name: "Critical", value: 3, color: "hsl(0, 84%, 60%)" },
];

const recentBatches = [
  { id: "BATCH-050", product: "Widget A", defects: 2, rate: "0.5%", decision: "ACCEPT", score: 98 },
  { id: "BATCH-049", product: "Widget C", defects: 8, rate: "2.0%", decision: "CONDITIONAL", score: 85 },
  { id: "BATCH-048", product: "Widget B", defects: 0, rate: "0%", decision: "ACCEPT", score: 100 },
  { id: "BATCH-047", product: "Widget A", defects: 15, rate: "3.8%", decision: "REJECTED", score: 62 },
  { id: "BATCH-046", product: "Widget D", defects: 3, rate: "0.6%", decision: "ACCEPT", score: 96 },
];

export function QualityIntelligenceDetail() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        {/* Defect Distribution */}
        <div>
          <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Defect Distribution</h4>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={defectData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={3} dataKey="value">
                {defectData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(0 0% 90%)", fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {defectData.map(d => (
              <div key={d.name} className="flex items-center gap-1.5 text-[10px]">
                <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                {d.name}: {d.value}
              </div>
            ))}
          </div>
        </div>

        {/* Quality Metrics */}
        <div className="space-y-4">
          <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Quality Metrics</h4>
          {[
            { label: "Overall Quality Score", value: 97.2, target: 95 },
            { label: "First Pass Yield", value: 94.8, target: 92 },
            { label: "Inspection Coverage", value: 100, target: 100 },
          ].map((m, i) => (
            <motion.div key={m.label} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }}>
              <div className="flex justify-between mb-1">
                <span className="text-xs">{m.label}</span>
                <span className="text-xs font-semibold">{m.value}%</span>
              </div>
              <Progress value={m.value} className="h-2" />
              <p className="text-[10px] text-muted-foreground mt-0.5">Target: {m.target}%</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Batches */}
      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Recent Inspections</h4>
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full text-xs">
            <thead><tr className="bg-muted/50">
              {["Batch", "Product", "Defects", "Rate", "Score", "Decision"].map(h => <th key={h} className="text-left p-2.5 font-medium text-muted-foreground">{h}</th>)}
            </tr></thead>
            <tbody>
              {recentBatches.map((b, i) => (
                <motion.tr key={b.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="border-t border-border hover:bg-muted/30 transition-colors">
                  <td className="p-2.5 font-medium">{b.id}</td>
                  <td className="p-2.5">{b.product}</td>
                  <td className="p-2.5">{b.defects}</td>
                  <td className="p-2.5">{b.rate}</td>
                  <td className="p-2.5"><span className={`font-semibold ${b.score >= 90 ? "text-[hsl(142,71%,45%)]" : b.score >= 70 ? "text-[hsl(38,92%,50%)]" : "text-[hsl(0,84%,60%)]"}`}>{b.score}</span></td>
                  <td className="p-2.5"><span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${b.decision === "ACCEPT" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : b.decision === "REJECTED" ? "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>{b.decision}</span></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
