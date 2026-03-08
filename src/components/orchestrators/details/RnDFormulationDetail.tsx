import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const formulations = [
  { id: "F-023", name: "FR-ABS Compound v7", strength: 48.2, cost: 142, efficiency: 94, status: "optimal" },
  { id: "F-022", name: "PA66-GF30 Blend", strength: 85.3, cost: 218, efficiency: 87, status: "testing" },
  { id: "F-021", name: "PP-Talc Composite", strength: 32.1, cost: 98, efficiency: 91, status: "optimal" },
  { id: "F-020", name: "PC-ABS Alloy", strength: 56.7, cost: 175, efficiency: 82, status: "rejected" },
];

export function RnDFormulationDetail() {
  const [evolving, setEvolving] = useState(false);
  const [generation, setGeneration] = useState(0);

  const handleEvolve = () => {
    setEvolving(true);
    let gen = 0;
    const interval = setInterval(() => {
      gen++;
      setGeneration(gen);
      if (gen >= 10) { clearInterval(interval); setEvolving(false); }
    }, 300);
  };

  return (
    <div className="space-y-6">
      {/* Genetic Algorithm Control */}
      <div className="p-4 rounded-xl border border-border bg-muted/30">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Dna className="w-4 h-4" />
            <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Genetic Optimization Engine</h4>
          </div>
          <Button size="sm" onClick={handleEvolve} disabled={evolving} className="h-8 text-xs rounded-lg">
            <Play className="w-3 h-3 mr-1" /> {evolving ? `Gen ${generation}/10…` : "Run Evolution"}
          </Button>
        </div>
        {generation > 0 && (
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-xs text-muted-foreground">Evolution Progress</span>
              <span className="text-xs font-medium">{generation * 10}%</span>
            </div>
            <Progress value={generation * 10} className="h-2" />
          </div>
        )}
      </div>

      {/* Formulations */}
      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Top Formulations</h4>
        <div className="space-y-3">
          {formulations.map((f, i) => (
            <motion.div key={f.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-4 rounded-xl border border-border hover:border-foreground/20 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold">{f.name}</p>
                  <p className="text-[10px] text-muted-foreground">{f.id}</p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${f.status === "optimal" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : f.status === "testing" ? "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]" : "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]"}`}>{f.status}</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <p className="text-[10px] text-muted-foreground">Tensile Strength</p>
                  <p className="text-sm font-medium">{f.strength} MPa</p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground">Cost</p>
                  <p className="text-sm font-medium">₹{f.cost}/kg</p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground">Efficiency</p>
                  <p className="text-sm font-medium">{f.efficiency}%</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
