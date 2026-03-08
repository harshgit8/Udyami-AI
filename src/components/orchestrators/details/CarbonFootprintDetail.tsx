import { motion } from "framer-motion";
import { Leaf } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const emissionsData = [
  { product: "Widget A", emissions: 2.1, target: 2.5 },
  { product: "Widget B", emissions: 3.4, target: 3.0 },
  { product: "Widget C", emissions: 1.8, target: 2.0 },
  { product: "Widget D", emissions: 4.2, target: 4.0 },
  { product: "Widget E", emissions: 2.7, target: 3.0 },
];

export function CarbonFootprintDetail() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Avg CO₂/Unit", value: "2.3 kg", color: "text-foreground" },
          { label: "Monthly Total", value: "4.8 tonnes", color: "text-foreground" },
          { label: "Sustainability Score", value: "A-", color: "text-[hsl(142,71%,45%)]" },
          { label: "vs Last Month", value: "-12%", color: "text-[hsl(142,71%,45%)]" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className={`text-lg font-semibold ${s.color}`}>{s.value}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">CO₂ Emissions per Product (kg/unit)</h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={emissionsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 90%)" />
            <XAxis dataKey="product" tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" />
            <YAxis tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" />
            <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(0 0% 90%)", fontSize: 12 }} />
            <Bar dataKey="emissions" fill="hsl(142, 71%, 45%)" radius={[4,4,0,0]} name="Actual" />
            <Bar dataKey="target" fill="hsl(0 0% 85%)" radius={[4,4,0,0]} name="Target" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="p-4 rounded-xl border border-border flex items-start gap-3">
        <Leaf className="w-4 h-4 text-[hsl(142,71%,45%)] mt-0.5" />
        <div>
          <h4 className="text-xs font-medium mb-1">AI Recommendation</h4>
          <p className="text-xs text-muted-foreground">Widget B exceeds its CO₂ target by 13%. Consider switching to recycled PP-Talc Composite (F-021) to reduce emissions by ~0.6 kg/unit.</p>
        </div>
      </div>
    </div>
  );
}
