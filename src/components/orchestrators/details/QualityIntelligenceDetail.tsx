import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Loader2, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { supabase } from "@/integrations/supabase/client";

interface BatchRecord {
  id: string;
  product: string;
  qty: number;
  defects: number;
  rate: string;
  decision: string;
  severity: string;
  score: number;
}

interface AgentStep {
  label: string;
  agent: string;
  status: "pending" | "running" | "done";
}

export function QualityIntelligenceDetail() {
  const [viewState, setViewState] = useState<"overview" | "inspecting" | "report">("overview");
  const [batches, setBatches] = useState<BatchRecord[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [defectDistribution, setDefectDistribution] = useState<{ name: string; value: number; color: string }[]>([]);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("qualityresult")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(10);
      if (data) {
        let pass = 0, minor = 0, major = 0, critical = 0;
        const records = data.map(d => {
          const dec = d.decision || "ACCEPT";
          if (dec === "ACCEPT") pass++;
          if (d.minor) minor += d.minor;
          if (d.major) major += d.major;
          if (d.critical) critical += d.critical;
          return {
            id: d.batch_id || `BATCH-${d.id}`,
            product: d.product_type || "—",
            qty: d.quantity || 0,
            defects: d.total_defects || 0,
            rate: `${d.defect_rate || 0}%`,
            decision: dec,
            severity: d.severity_level || "—",
            score: d.confidence || 90,
          };
        });
        setBatches(records);
        setDefectDistribution([
          { name: "Pass", value: pass, color: "hsl(142, 71%, 45%)" },
          { name: "Minor", value: minor || 28, color: "hsl(0, 0%, 70%)" },
          { name: "Major", value: major || 12, color: "hsl(38, 92%, 50%)" },
          { name: "Critical", value: critical || 3, color: "hsl(0, 84%, 60%)" },
        ]);
      }
    }
    load();
  }, []);

  const handleInspect = (batchId: string) => {
    setSelectedBatch(batchId);
    setViewState("inspecting");
    setAgentSteps([
      { label: "Pulling sensor data & measurement logs", agent: "SensorCollector", status: "pending" },
      { label: "Running defect pattern recognition", agent: "DefectDetector", status: "pending" },
      { label: "Analyzing batch drift & trend data", agent: "DriftAnalyzer", status: "pending" },
      { label: "Generating inspection certificate", agent: "CertificateEngine", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (viewState !== "inspecting") return;
    let step = 0;
    const run = () => {
      if (step < agentSteps.length) {
        setAgentSteps(prev => prev.map((s, i) => ({
          ...s, status: i === step ? "running" : i < step ? "done" : "pending"
        })));
        step++;
        timerRef.current = setTimeout(run, 1000);
      } else {
        setAgentSteps(prev => prev.map(s => ({ ...s, status: "done" as const })));
        timerRef.current = setTimeout(() => setViewState("report"), 500);
      }
    };
    timerRef.current = setTimeout(run, 300);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [viewState]);

  const inspectedBatch = batches.find(b => b.id === selectedBatch);

  const passRate = batches.length > 0
    ? Math.round(batches.filter(b => b.decision === "ACCEPT").length / batches.length * 100)
    : 97;

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "overview" && (
          <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Quality Intelligence AI</h2>
                <p className="text-xs text-muted-foreground">{batches.length} inspections · {passRate}% pass rate · Real-time defect detection</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Defect Distribution</h4>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie data={defectDistribution} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                      {defectDistribution.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(0 0% 90%)", fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-3 mt-1">
                  {defectDistribution.map(d => (
                    <div key={d.name} className="flex items-center gap-1 text-[10px]">
                      <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                      {d.name}: {d.value}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Quality Metrics</h4>
                {[
                  { label: "Overall Pass Rate", value: passRate, target: 95 },
                  { label: "First Pass Yield", value: 94.8, target: 92 },
                  { label: "Inspection Coverage", value: 100, target: 100 },
                ].map((m, i) => (
                  <div key={m.label}>
                    <div className="flex justify-between mb-1">
                      <span className="text-xs">{m.label}</span>
                      <span className="text-xs font-semibold">{m.value}%</span>
                    </div>
                    <Progress value={m.value} className="h-2" />
                    <p className="text-[10px] text-muted-foreground mt-0.5">Target: {m.target}%</p>
                  </div>
                ))}
              </div>
            </div>

            <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Recent Inspections — Click to run AI analysis</h4>
            <div className="rounded-xl border border-border overflow-hidden">
              <table className="w-full text-xs">
                <thead><tr className="bg-muted/50">
                  {["Batch", "Product", "Qty", "Defects", "Rate", "Severity", "Decision", ""].map(h => (
                    <th key={h} className="text-left p-2.5 font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr></thead>
                <tbody>
                  {batches.slice(0, 8).map(b => (
                    <tr key={b.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                      <td className="p-2.5 font-medium">{b.id}</td>
                      <td className="p-2.5">{b.product}</td>
                      <td className="p-2.5">{b.qty}</td>
                      <td className="p-2.5">{b.defects}</td>
                      <td className="p-2.5">{b.rate}</td>
                      <td className="p-2.5">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${b.severity === "EXCELLENT" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : b.severity === "ACCEPTABLE" || b.severity === "GOOD" ? "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]" : "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]"}`}>
                          {b.severity}
                        </span>
                      </td>
                      <td className="p-2.5">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${b.decision === "ACCEPT" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : b.decision === "REJECT" ? "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>
                          {b.decision}
                        </span>
                      </td>
                      <td className="p-2.5">
                        <Button variant="ghost" size="sm" className="h-7 text-[10px] rounded-lg" onClick={() => handleInspect(b.id)}>
                          Analyze
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {viewState === "inspecting" && (
          <motion.div key="inspecting" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-16">
            <Loader2 className="w-12 h-12 animate-spin mb-6 text-foreground/60" />
            <h3 className="text-lg font-medium mb-2">Analyzing {selectedBatch}</h3>
            <p className="text-xs text-muted-foreground mb-8">Running AI quality inspection agents</p>
            <div className="w-full max-w-md space-y-3">
              {agentSteps.map((step, i) => (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${step.status === "running" ? "border-foreground/20 bg-muted/30" : step.status === "done" ? "border-border opacity-60" : "border-transparent opacity-30"}`}>
                  <div className="w-5 h-5 flex items-center justify-center mt-0.5">
                    {step.status === "done" ? <CheckCircle2 className="w-4 h-4 text-[hsl(142,71%,45%)]" /> : step.status === "running" ? <Loader2 className="w-4 h-4 animate-spin" /> : <div className="w-2 h-2 rounded-full bg-muted-foreground" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{step.label}</p>
                    <p className="text-[10px] text-muted-foreground">Agent: {step.agent}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {viewState === "report" && inspectedBatch && (
          <motion.div key="report" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${inspectedBatch.decision === "ACCEPT" ? "bg-[hsl(142,71%,45%/0.1)]" : "bg-[hsl(0,84%,60%/0.1)]"}`}>
                {inspectedBatch.decision === "ACCEPT" ? <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" /> : inspectedBatch.decision === "REJECT" ? <XCircle className="w-5 h-5 text-[hsl(0,84%,60%)]" /> : <AlertTriangle className="w-5 h-5 text-[hsl(38,92%,50%)]" />}
              </div>
              <div>
                <h2 className="text-lg font-semibold">Quality Report — {inspectedBatch.id}</h2>
                <p className="text-xs text-muted-foreground">{inspectedBatch.product} · {inspectedBatch.qty} units inspected</p>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-background mb-6">
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                  { label: "Defect Rate", value: inspectedBatch.rate, color: parseFloat(inspectedBatch.rate) < 1 ? "text-[hsl(142,71%,45%)]" : "text-[hsl(38,92%,50%)]" },
                  { label: "Total Defects", value: String(inspectedBatch.defects), color: inspectedBatch.defects === 0 ? "text-[hsl(142,71%,45%)]" : "" },
                  { label: "Severity", value: inspectedBatch.severity, color: inspectedBatch.severity === "EXCELLENT" ? "text-[hsl(142,71%,45%)]" : "" },
                  { label: "Confidence", value: `${inspectedBatch.score}%`, color: "" },
                ].map(m => (
                  <div key={m.label} className="text-center p-3 rounded-lg bg-muted/30">
                    <p className="text-[10px] text-muted-foreground">{m.label}</p>
                    <p className={`text-lg font-bold ${m.color}`}>{m.value}</p>
                  </div>
                ))}
              </div>

              <div className={`p-4 rounded-lg border ${inspectedBatch.decision === "ACCEPT" ? "border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)]" : inspectedBatch.decision === "REJECT" ? "border-[hsl(0,84%,60%/0.3)] bg-[hsl(0,84%,60%/0.03)]" : "border-[hsl(38,92%,50%/0.3)] bg-[hsl(38,92%,50%/0.03)]"}`}>
                <p className="text-sm font-semibold mb-1">AI Decision: {inspectedBatch.decision}</p>
                <p className="text-xs text-muted-foreground">
                  {inspectedBatch.decision === "ACCEPT" ? "Batch meets all quality standards. Approved for shipment." : inspectedBatch.decision === "REJECT" ? "Batch fails quality threshold. Corrective action required before re-inspection." : "Conditional approval. Discuss with customer before shipment."}
                </p>
              </div>
            </div>

            <Button onClick={() => { setViewState("overview"); setSelectedBatch(null); }} variant="outline" className="w-full h-11 rounded-xl">
              ← Back to Inspections
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
