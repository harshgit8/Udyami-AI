import { useState } from "react";
import { motion } from "framer-motion";
import { Play, AlertTriangle, TrendingDown, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

const scenarios = [
  { label: "Machine Failure", value: "machine_failure" },
  { label: "Material Shortage", value: "material_shortage" },
  { label: "Rush Order", value: "rush_order" },
  { label: "Price Increase", value: "price_increase" },
];

interface SimResult {
  profitImpact: string;
  riskScore: number;
  utilization: number;
  recommendation: string;
  timeline: string;
}

const mockResults: Record<string, SimResult> = {
  machine_failure: { profitImpact: "-₹4.2L", riskScore: 78, utilization: 72, recommendation: "Shift load to M2 and M5. Schedule emergency maintenance for M1 during night shift.", timeline: "Recovery in 18 hours" },
  material_shortage: { profitImpact: "-₹2.8L", riskScore: 65, utilization: 85, recommendation: "Switch to alternate supplier S3. Prioritize high-margin orders.", timeline: "Alternate supply in 3 days" },
  rush_order: { profitImpact: "+₹1.5L", riskScore: 42, utilization: 98, recommendation: "Accept order. Reschedule Batch-048 to next week. Overtime approved for Line B.", timeline: "Delivery in 5 days" },
  price_increase: { profitImpact: "-₹3.1L", riskScore: 55, utilization: 94, recommendation: "Negotiate bulk contract with S1. Lock current prices for 90 days.", timeline: "Impact starts in 2 weeks" },
};

export function WhatIfSimulatorDetail() {
  const [scenario, setScenario] = useState("machine_failure");
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<SimResult | null>(null);

  const handleSimulate = () => {
    setSimulating(true);
    setResult(null);
    setTimeout(() => { setSimulating(false); setResult(mockResults[scenario]); }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Input Panel */}
      <div className="p-4 rounded-xl border border-border bg-muted/30">
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Scenario Configuration</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Scenario Type</label>
            <Select value={scenario} onValueChange={setScenario}>
              <SelectTrigger className="h-9 text-sm rounded-lg"><SelectValue /></SelectTrigger>
              <SelectContent>{scenarios.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent>
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
            <Button onClick={handleSimulate} disabled={simulating} className="w-full h-9 text-xs rounded-lg">
              {simulating ? <><AlertTriangle className="w-3 h-3 mr-1 animate-pulse" /> Simulating…</> : <><Play className="w-3 h-3 mr-1" /> Run Simulation</>}
            </Button>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-muted/50 text-center">
              <p className={`text-xl font-bold ${result.profitImpact.startsWith("-") ? "text-[hsl(0,84%,60%)]" : "text-[hsl(142,71%,45%)]"}`}>{result.profitImpact}</p>
              <p className="text-[10px] text-muted-foreground mt-1">Profit Impact</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/50 text-center">
              <p className="text-xl font-bold">{result.riskScore}%</p>
              <p className="text-[10px] text-muted-foreground mt-1">Risk Score</p>
              <Progress value={result.riskScore} className="h-1.5 mt-2" />
            </div>
            <div className="p-4 rounded-xl bg-muted/50 text-center">
              <p className="text-xl font-bold">{result.utilization}%</p>
              <p className="text-[10px] text-muted-foreground mt-1">Machine Utilization</p>
              <Progress value={result.utilization} className="h-1.5 mt-2" />
            </div>
          </div>
          <div className="p-4 rounded-xl border border-border">
            <h4 className="text-xs font-medium mb-2">AI Recommendation</h4>
            <p className="text-sm text-muted-foreground">{result.recommendation}</p>
            <p className="text-xs text-[hsl(142,71%,45%)] mt-2 font-medium">{result.timeline}</p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
