import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FlaskConical, Dna, Play, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { supabase } from "@/integrations/supabase/client";

interface FormulationRecord {
  id: string;
  polymer: string;
  additives: string;
  cost: number;
  tensile: number;
  ul94: string;
  rohs: string;
  reach: string;
  recommendation: string;
}

interface AgentStep {
  label: string;
  agent: string;
  status: "pending" | "running" | "done";
}

export function RnDFormulationDetail() {
  const [viewState, setViewState] = useState<"lab" | "evolving" | "result">("lab");
  const [formulations, setFormulations] = useState<FormulationRecord[]>([]);
  const [generation, setGeneration] = useState(0);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [selectedFormulation, setSelectedFormulation] = useState<FormulationRecord | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("rndresult")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(8);
      if (data) {
        setFormulations(data.map(d => ({
          id: d.formulation_id || `FORM-${d.id}`,
          polymer: d.base_polymer || "—",
          additives: d.key_additives || "—",
          cost: d.cost_kg || 0,
          tensile: d.tensile_mpa || 0,
          ul94: d.ul94_rating || "—",
          rohs: d.rohs || "—",
          reach: d.reach || "—",
          recommendation: d.recommendation || "—",
        })));
      }
    }
    load();
  }, []);

  const handleEvolve = () => {
    setViewState("evolving");
    setGeneration(0);
    setAgentSteps([
      { label: "Loading compound database (50,000+ entries)", agent: "CompoundLibrary", status: "pending" },
      { label: "Running genetic algorithm optimization", agent: "GeneticOptimizer", status: "pending" },
      { label: "Evaluating compliance: RoHS, REACH, UL94", agent: "ComplianceChecker", status: "pending" },
      { label: "Cost-performance Pareto analysis", agent: "ParetoAnalyzer", status: "pending" },
      { label: "Generating formulation report", agent: "ReportGenerator", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (viewState !== "evolving") return;
    let step = 0;
    let gen = 0;
    const genInterval = setInterval(() => {
      gen++;
      setGeneration(gen);
      if (gen >= 10) clearInterval(genInterval);
    }, 400);

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
    return () => {
      clearInterval(genInterval);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [viewState]);

  const pilotReady = formulations.filter(f => f.recommendation.includes("PILOT") || f.recommendation.includes("PROCEED"));
  const labTesting = formulations.filter(f => f.recommendation.includes("LABORATORY") || f.recommendation.includes("TESTING"));

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "lab" && (
          <motion.div key="lab" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                  <FlaskConical className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">R&D Formulation AI</h2>
                  <p className="text-xs text-muted-foreground">{formulations.length} formulations · {pilotReady.length} pilot-ready · {labTesting.length} in lab testing</p>
                </div>
              </div>
              <Button onClick={handleEvolve} className="gap-2 rounded-xl">
                <Dna className="w-4 h-4" /> Run Genetic Evolution
              </Button>
            </div>

            <div className="grid grid-cols-4 gap-3 mb-6">
              {[
                { label: "Total Formulations", value: formulations.length },
                { label: "Pilot Ready", value: pilotReady.length },
                { label: "Lab Testing", value: labTesting.length },
                { label: "Avg Cost", value: `₹${formulations.length > 0 ? Math.round(formulations.reduce((a, b) => a + b.cost, 0) / formulations.length) : 0}/kg` },
              ].map(m => (
                <div key={m.label} className="p-3 rounded-xl bg-muted/30 text-center">
                  <p className="text-[10px] text-muted-foreground">{m.label}</p>
                  <p className="text-lg font-bold">{m.value}</p>
                </div>
              ))}
            </div>

            <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Formulations Database</h4>
            <div className="space-y-2.5">
              {formulations.map((f, i) => (
                <motion.div key={f.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  className="p-4 rounded-xl border border-border hover:border-foreground/10 transition-all cursor-pointer"
                  onClick={() => setSelectedFormulation(selectedFormulation?.id === f.id ? null : f)}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="text-sm font-semibold">{f.polymer} — {f.additives}</p>
                      <p className="text-[10px] text-muted-foreground">{f.id}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${f.recommendation.includes("PILOT") || f.recommendation.includes("PROCEED") ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : f.recommendation.includes("CAUTION") ? "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]" : "bg-muted text-muted-foreground"}`}>
                      {f.recommendation.includes("PILOT") || f.recommendation.includes("PROCEED") ? "Pilot Ready" : f.recommendation.includes("CAUTION") ? "Caution" : "Lab Testing"}
                    </span>
                  </div>
                  <div className="grid grid-cols-5 gap-2 text-xs">
                    <div><span className="text-muted-foreground">Cost:</span> ₹{f.cost}/kg</div>
                    <div><span className="text-muted-foreground">Tensile:</span> {f.tensile} MPa</div>
                    <div><span className="text-muted-foreground">UL94:</span> {f.ul94}</div>
                    <div><span className="text-muted-foreground">RoHS:</span> {f.rohs}</div>
                    <div><span className="text-muted-foreground">REACH:</span> {f.reach}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {viewState === "evolving" && (
          <motion.div key="evolving" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-12">
            <div className="relative mb-6">
              <Dna className="w-12 h-12 animate-pulse" />
            </div>
            <h3 className="text-lg font-medium mb-2">Genetic Algorithm Running</h3>
            <p className="text-xs text-muted-foreground mb-2">Generation {generation}/10 · Evolving optimal formulations</p>
            <Progress value={generation * 10} className="h-2 w-48 mb-8" />

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

        {viewState === "result" && (
          <motion.div key="result" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[hsl(142,71%,45%/0.1)] flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Evolution Complete</h2>
                <p className="text-xs text-muted-foreground">10 generations · 3 optimal candidates identified</p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              {[
                { name: "FR-ABS Optimized v8", polymer: "ABS + FR Masterbatch", cost: 135, tensile: 52, ul94: "V-0", confidence: "96%" },
                { name: "PVC K70 Low-Cost", polymer: "PVC K70 + CaCO3", cost: 54, tensile: 48, ul94: "HB", confidence: "92%" },
                { name: "PA66-GF30 High-Strength", polymer: "PA66 + 30% Glass Fiber", cost: 210, tensile: 88, ul94: "V-0", confidence: "89%" },
              ].map((f, i) => (
                <div key={i} className={`p-4 rounded-xl border ${i === 0 ? "border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)]" : "border-border"}`}>
                  <div className="flex justify-between mb-2">
                    <div>
                      <p className="text-sm font-semibold">{f.name}</p>
                      <p className="text-[10px] text-muted-foreground">{f.polymer}</p>
                    </div>
                    <span className="text-xs font-medium text-[hsl(142,71%,45%)]">Confidence: {f.confidence}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div className="p-2 rounded-lg bg-muted/30 text-center">
                      <p className="text-muted-foreground">Cost</p>
                      <p className="font-semibold">₹{f.cost}/kg</p>
                    </div>
                    <div className="p-2 rounded-lg bg-muted/30 text-center">
                      <p className="text-muted-foreground">Tensile</p>
                      <p className="font-semibold">{f.tensile} MPa</p>
                    </div>
                    <div className="p-2 rounded-lg bg-muted/30 text-center">
                      <p className="text-muted-foreground">UL94</p>
                      <p className="font-semibold">{f.ul94}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <Button onClick={() => setViewState("lab")} variant="outline" className="w-full h-11 rounded-xl">
              ← Back to Lab
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
