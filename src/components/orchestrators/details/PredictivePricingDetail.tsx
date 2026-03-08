import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const priceHistory = [
  { month: "Oct", actual: 680, recommended: 710 },
  { month: "Nov", actual: 695, recommended: 720 },
  { month: "Dec", actual: 710, recommended: 735 },
  { month: "Jan", actual: 720, recommended: 745 },
  { month: "Feb", actual: 730, recommended: 755 },
  { month: "Mar", actual: 735, recommended: 760 },
];

export function PredictivePricingDetail() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(false);

  return (
    <div className="space-y-6">
      {/* Input */}
      <div className="p-4 rounded-xl border border-border bg-muted/30">
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Price Analysis Input</h4>
        <div className="grid grid-cols-4 gap-3">
          <div><label className="text-[10px] font-medium text-muted-foreground mb-1 block">Product Cost (₹/unit)</label><Input defaultValue="520" className="h-9 text-sm rounded-lg" /></div>
          <div><label className="text-[10px] font-medium text-muted-foreground mb-1 block">Market Demand</label><Input defaultValue="High" className="h-9 text-sm rounded-lg" /></div>
          <div><label className="text-[10px] font-medium text-muted-foreground mb-1 block">Competitor Price (₹)</label><Input defaultValue="750" className="h-9 text-sm rounded-lg" /></div>
          <div className="flex items-end"><Button className="w-full h-9 text-xs rounded-lg" onClick={() => { setAnalyzing(true); setTimeout(() => { setAnalyzing(false); setResult(true); }, 1500); }} disabled={analyzing}>{analyzing ? "Analyzing…" : <><Sparkles className="w-3 h-3 mr-1" /> Predict</>}</Button></div>
        </div>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-[hsl(142,71%,45%/0.05)] border border-[hsl(142,71%,45%/0.2)] text-center">
              <p className="text-2xl font-bold text-[hsl(142,71%,45%)]">₹760</p>
              <p className="text-[10px] text-muted-foreground mt-1">Recommended Price</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/50 text-center">
              <p className="text-2xl font-bold">31.5%</p>
              <p className="text-[10px] text-muted-foreground mt-1">Profit Margin</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/50 text-center">
              <p className="text-2xl font-bold flex items-center justify-center"><TrendingUp className="w-5 h-5 mr-1 text-[hsl(142,71%,45%)]" />High</p>
              <p className="text-[10px] text-muted-foreground mt-1">Demand Forecast</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Price Trend */}
      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Price Trend: Actual vs Recommended</h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={priceHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 90%)" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" />
            <YAxis tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" domain={[600, 800]} />
            <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(0 0% 90%)", fontSize: 12 }} />
            <Bar dataKey="actual" fill="hsl(0 0% 80%)" radius={[4,4,0,0]} name="Actual" />
            <Bar dataKey="recommended" fill="hsl(0 0% 9%)" radius={[4,4,0,0]} name="AI Recommended" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
