import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, AlertTriangle, Loader2, CheckCircle2, Dices } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

const scenarios = [
  { label: "Machine Failure", value: "machine_failure", icon: "⚙️" },
  { label: "Material Shortage", value: "material_shortage", icon: "📦" },
  { label: "Rush Order", value: "rush_order", icon: "⚡" },
  { label: "Price Increase", value: "price_increase", icon: "📈" },
];

interface AgentStep { label: string; agent: string; status: "pending" | "running" | "done"; }

interface SimResult {
  profitImpact: string; positive: boolean;
  riskScore: number; utilization: number;
  recommendation: string; timeline: string;
  affectedOrders: string[];
  mitigationSteps: string[];
}

const mockResults: Record<string, SimResult> = {
  machine_failure: { profitImpact: "-₹4.2L", positive: false, riskScore: 78, utilization: 72, recommendation: "Shift load to M2 and M5. Schedule emergency maintenance for M1 during night shift. Prioritize ORD-001 and ORD-003.", timeline: "Recovery in 18 hours", affectedOrders: ["ORD-001", "ORD-003", "ORD-007"], mitigationSteps: ["Reroute M1 jobs to M2 (88% capacity available)", "Call maintenance team — ETA 4 hours", "Notify Acme Corp of 6-hour delay on ORD-001"] },
  material_shortage: { profitImpact: "-₹2.8L", positive: false, riskScore: 65, utilization: 85, recommendation: "Switch to alternate supplier S3 for ABS resin. Prioritize high-margin orders. Defer low-priority batches.", timeline: "Alternate supply arrives in 3 days", affectedOrders: ["ORD-005", "ORD-012", "ORD-018"], mitigationSteps: ["Contact supplier S3 — spot purchase 500kg ABS", "Reschedule ORD-018 (low priority) to next week", "Use 200kg buffer stock for ORD-005"] },
  rush_order: { profitImpact: "+₹1.5L", positive: true, riskScore: 42, utilization: 98, recommendation: "Accept rush order. Reschedule Batch-048 to next week. Overtime approved for Extrusion Line B.", timeline: "Delivery possible in 5 days", affectedOrders: ["BATCH-048", "ORD-022"], mitigationSteps: ["Approve 8 hours overtime for Line B team", "Reschedule BATCH-048 (non-urgent) to Monday", "Fast-track quality inspection for rush batch"] },
  price_increase: { profitImpact: "-₹3.1L", positive: false, riskScore: 55, utilization: 94, recommendation: "Negotiate bulk contract with S1 at current rates. Lock prices for 90 days. Update quotation templates.", timeline: "Price impact starts in 2 weeks", affectedOrders: ["All new quotations"], mitigationSteps: ["Lock 90-day contract with Supplier S1", "Increase buffer stock by 20% at current prices", "Revise quotation margin from 25% to 28%"] },
};

export function WhatIfSimulatorDetail() {
  const [viewState, setViewState] = useState<"config" | "simulating" | "result">("config");
  const [scenario, setScenario] = useState("machine_failure");
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [result, setResult] = useState<SimResult | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const handleSimulate = () => {
    setViewState("simulating");
    setAgentSteps([
      { label: "Loading current production state", agent: "StateLoader", status: "pending" },
      { label: `Injecting scenario: ${scenarios.find(s => s.value === scenario)?.label}`, agent: "ScenarioInjector", status: "pending" },
      { label: "Running Monte Carlo simulation (1000 iterations)", agent: "SimulationEngine", status: "pending" },
      { label: "Calculating financial & operational impact", agent: "ImpactAnalyzer", status: "pending" },
      { label: "Generating mitigation recommendations", agent: "MitigationPlanner", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (viewState !== "simulating") return;
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
        setResult(mockResults[scenario]);
        timerRef.current = setTimeout(() => setViewState("result"), 500);
      }
    };
    timerRef.current = setTimeout(run, 300);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [viewState]);

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "config" && (
          <motion.div key="config" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                <Dices className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">What-If Scenario Simulator</h2>
                <p className="text-xs text-muted-foreground">Simulate disruptions before they happen</p>
              </div>
            </div>

            <div className="p-5 rounded-xl border border-border bg-muted/20 mb-6">
              <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">Configure Scenario</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Scenario Type</label>
                  <Select value={scenario} onValueChange={setScenario}>
                    <SelectTrigger className="h-9 text-sm rounded-lg"><SelectValue /></SelectTrigger>
                    <SelectContent>{scenarios.map(s => <SelectItem key={s.value} value={s.value}>{s.icon} {s.label}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Affected Machine</label>
                  <Select defaultValue="M1">
                    <SelectTrigger className="h-9 text-sm rounded-lg"><SelectValue /></SelectTrigger>
                    <SelectContent>{["M1","M2","M3","M4","M5"].map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Duration (hours)</label>
                  <Input type="number" defaultValue="8" className="h-9 text-sm rounded-lg" />
                </div>
                <div className="flex items-end">
                  <Button onClick={handleSimulate} className="w-full h-9 text-xs rounded-lg gap-1.5">
                    <Play className="w-3.5 h-3.5" /> Run Simulation
                  </Button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-2">
              {scenarios.map(s => (
                <button key={s.value} onClick={() => { setScenario(s.value); handleSimulate(); }}
                  className="p-3 rounded-xl border border-border bg-background hover:bg-muted/30 transition-all text-center">
                  <span className="text-lg block mb-1">{s.icon}</span>
                  <span className="text-xs font-medium">{s.label}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {viewState === "simulating" && (
          <motion.div key="simulating" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-16">
            <AlertTriangle className="w-12 h-12 animate-pulse mb-6 text-[hsl(38,92%,50%)]" />
            <h3 className="text-lg font-medium mb-2">Simulating: {scenarios.find(s => s.value === scenario)?.label}</h3>
            <p className="text-xs text-muted-foreground mb-8">Running 1000 iterations...</p>
            <div className="w-full max-w-md space-y-3">
              {agentSteps.map((step, i) => (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${step.status === "running" ? "border-[hsl(38,92%,50%/0.3)] bg-[hsl(38,92%,50%/0.05)]" : step.status === "done" ? "border-border opacity-60" : "border-transparent opacity-30"}`}>
                  <div className="w-5 h-5 flex items-center justify-center mt-0.5">
                    {step.status === "done" ? <CheckCircle2 className="w-4 h-4 text-[hsl(142,71%,45%)]" /> : step.status === "running" ? <Loader2 className="w-4 h-4 animate-spin text-[hsl(38,92%,50%)]" /> : <div className="w-2 h-2 rounded-full bg-muted-foreground" />}
                  </div>
                  <div><p className="text-sm font-medium">{step.label}</p><p className="text-[10px] text-muted-foreground">Agent: {step.agent}</p></div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {viewState === "result" && result && (
          <motion.div key="result" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${result.positive ? "bg-[hsl(142,71%,45%/0.1)]" : "bg-[hsl(38,92%,50%/0.1)]"}`}>
                  {result.positive ? <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" /> : <AlertTriangle className="w-5 h-5 text-[hsl(38,92%,50%)]" />}
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Simulation Complete</h2>
                  <p className="text-xs text-muted-foreground">{scenarios.find(s => s.value === scenario)?.label} · {result.timeline}</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => { setViewState("config"); setResult(null); }} className="rounded-xl">
                New Simulation
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="p-4 rounded-xl bg-muted/30 text-center">
                <p className={`text-xl font-bold ${result.positive ? "text-[hsl(142,71%,45%)]" : "text-[hsl(0,84%,60%)]"}`}>{result.profitImpact}</p>
                <p className="text-[10px] text-muted-foreground mt-1">Profit Impact</p>
              </div>
              <div className="p-4 rounded-xl bg-muted/30 text-center">
                <p className="text-xl font-bold">{result.riskScore}%</p>
                <p className="text-[10px] text-muted-foreground mt-1">Risk Score</p>
                <Progress value={result.riskScore} className="h-1.5 mt-2" />
              </div>
              <div className="p-4 rounded-xl bg-muted/30 text-center">
                <p className="text-xl font-bold">{result.utilization}%</p>
                <p className="text-[10px] text-muted-foreground mt-1">Machine Utilization</p>
                <Progress value={result.utilization} className="h-1.5 mt-2" />
              </div>
            </div>

            <div className="p-4 rounded-xl border border-border mb-4">
              <h4 className="text-xs font-semibold mb-2">AI Recommendation</h4>
              <p className="text-sm text-muted-foreground">{result.recommendation}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl border border-border">
                <h4 className="text-xs font-semibold mb-2">Affected Orders</h4>
                <div className="space-y-1.5">
                  {result.affectedOrders.map(o => (
                    <div key={o} className="text-xs p-2 rounded-lg bg-[hsl(0,84%,60%/0.05)] border border-[hsl(0,84%,60%/0.1)] font-medium">{o}</div>
                  ))}
                </div>
              </div>
              <div className="p-4 rounded-xl border border-border">
                <h4 className="text-xs font-semibold mb-2">Mitigation Steps</h4>
                <div className="space-y-1.5">
                  {result.mitigationSteps.map((s, i) => (
                    <div key={i} className="text-xs p-2 rounded-lg bg-[hsl(142,71%,45%/0.05)] border border-[hsl(142,71%,45%/0.1)]">
                      <span className="font-medium mr-1">{i + 1}.</span> {s}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
