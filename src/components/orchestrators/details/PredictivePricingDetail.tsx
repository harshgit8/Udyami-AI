import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, Sparkles, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface AgentStep { label: string; agent: string; status: "pending" | "running" | "done"; }

const priceHistory = [
  { month: "Oct", actual: 680, recommended: 710 },
  { month: "Nov", actual: 695, recommended: 720 },
  { month: "Dec", actual: 710, recommended: 735 },
  { month: "Jan", actual: 720, recommended: 745 },
  { month: "Feb", actual: 730, recommended: 755 },
  { month: "Mar", actual: 735, recommended: 760 },
];

export function PredictivePricingDetail() {
  const [viewState, setViewState] = useState<"input" | "analyzing" | "result">("input");
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [productCost, setProductCost] = useState("520");
  const [demand, setDemand] = useState("high");
  const [competitorPrice, setCompetitorPrice] = useState("750");
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const handleAnalyze = () => {
    setViewState("analyzing");
    setAgentSteps([
      { label: "Fetching real-time cost data from database", agent: "CostCollector", status: "pending" },
      { label: "Analyzing market demand signals", agent: "DemandAnalyzer", status: "pending" },
      { label: "Running competitor price benchmarking", agent: "CompetitorTracker", status: "pending" },
      { label: "Calculating optimal price point", agent: "PriceOptimizer", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (viewState !== "analyzing") return;
    let step = 0;
    const run = () => {
      if (step < agentSteps.length) {
        setAgentSteps(prev => prev.map((s, i) => ({
          ...s, status: i === step ? "running" : i < step ? "done" : "pending"
        })));
        step++;
        timerRef.current = setTimeout(run, 900);
      } else {
        setAgentSteps(prev => prev.map(s => ({ ...s, status: "done" as const })));
        timerRef.current = setTimeout(() => setViewState("result"), 500);
      }
    };
    timerRef.current = setTimeout(run, 300);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [viewState]);

  const cost = parseFloat(productCost) || 520;
  const competitor = parseFloat(competitorPrice) || 750;
  const recommendedPrice = Math.round(cost * 1.46);
  const margin = Math.round((1 - cost / recommendedPrice) * 100 * 10) / 10;

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "input" && (
          <motion.div key="input" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center"><TrendingUp className="w-6 h-6" /></div>
              <div>
                <h2 className="text-lg font-semibold">Predictive Pricing Engine</h2>
                <p className="text-xs text-muted-foreground">AI-optimized pricing based on cost, demand, and competition</p>
              </div>
            </div>

            <div className="p-5 rounded-xl border border-border bg-muted/20 mb-6">
              <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">Price Analysis Input</h4>
              <div className="grid grid-cols-4 gap-3">
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Product Cost (₹/unit)</label>
                  <Input value={productCost} onChange={e => setProductCost(e.target.value)} className="h-9 text-sm rounded-lg" />
                </div>
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Market Demand</label>
                  <Select value={demand} onValueChange={setDemand}>
                    <SelectTrigger className="h-9 text-sm rounded-lg"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Competitor Price (₹)</label>
                  <Input value={competitorPrice} onChange={e => setCompetitorPrice(e.target.value)} className="h-9 text-sm rounded-lg" />
                </div>
                <div className="flex items-end">
                  <Button onClick={handleAnalyze} className="w-full h-9 text-xs rounded-lg gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> Predict Price
                  </Button>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Historical: Actual vs AI Recommended</h4>
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
          </motion.div>
        )}

        {viewState === "analyzing" && (
          <motion.div key="analyzing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-16">
            <Loader2 className="w-12 h-12 animate-spin mb-6 text-foreground/60" />
            <h3 className="text-lg font-medium mb-8">Analyzing Optimal Price</h3>
            <div className="w-full max-w-md space-y-3">
              {agentSteps.map((step, i) => (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${step.status === "running" ? "border-foreground/20 bg-muted/30" : step.status === "done" ? "border-border opacity-60" : "border-transparent opacity-30"}`}>
                  <div className="w-5 h-5 flex items-center justify-center mt-0.5">
                    {step.status === "done" ? <CheckCircle2 className="w-4 h-4 text-[hsl(142,71%,45%)]" /> : step.status === "running" ? <Loader2 className="w-4 h-4 animate-spin" /> : <div className="w-2 h-2 rounded-full bg-muted-foreground" />}
                  </div>
                  <div><p className="text-sm font-medium">{step.label}</p><p className="text-[10px] text-muted-foreground">Agent: {step.agent}</p></div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {viewState === "result" && (
          <motion.div key="result" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[hsl(142,71%,45%/0.1)] flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Price Recommendation</h2>
                  <p className="text-xs text-muted-foreground">Based on cost ₹{cost}, {demand} demand, competitor ₹{competitor}</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => setViewState("input")} className="rounded-xl">New Analysis</Button>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="p-5 rounded-xl bg-[hsl(142,71%,45%/0.05)] border border-[hsl(142,71%,45%/0.2)] text-center">
                <p className="text-2xl font-bold text-[hsl(142,71%,45%)]">₹{recommendedPrice}</p>
                <p className="text-[10px] text-muted-foreground mt-1">Recommended Price</p>
              </div>
              <div className="p-5 rounded-xl bg-muted/30 text-center">
                <p className="text-2xl font-bold">{margin}%</p>
                <p className="text-[10px] text-muted-foreground mt-1">Profit Margin</p>
              </div>
              <div className="p-5 rounded-xl bg-muted/30 text-center">
                <p className="text-2xl font-bold flex items-center justify-center"><TrendingUp className="w-5 h-5 mr-1 text-[hsl(142,71%,45%)]" />{demand === "high" ? "High" : demand === "medium" ? "Med" : "Low"}</p>
                <p className="text-[10px] text-muted-foreground mt-1">Demand Forecast</p>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-border mb-4">
              <h4 className="text-xs font-semibold mb-2">Pricing Strategy</h4>
              <p className="text-sm text-muted-foreground">At ₹{recommendedPrice}/unit, you're positioned {recommendedPrice < competitor ? `₹${competitor - recommendedPrice} below` : `₹${recommendedPrice - competitor} above`} the competitor while maintaining a healthy {margin}% margin. {demand === "high" ? "High demand supports premium pricing." : "Consider volume discounts to drive sales."}</p>
            </div>

            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 90%)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" />
                <YAxis tick={{ fontSize: 11 }} stroke="hsl(0 0% 45%)" domain={[600, 800]} />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(0 0% 90%)", fontSize: 12 }} />
                <Bar dataKey="actual" fill="hsl(0 0% 80%)" radius={[4,4,0,0]} name="Actual" />
                <Bar dataKey="recommended" fill="hsl(0 0% 9%)" radius={[4,4,0,0]} name="AI Recommended" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
