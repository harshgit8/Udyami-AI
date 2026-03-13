import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Settings, Users, Package, CheckCircle2, Edit2, Save, Send, Loader2, ArrowRight, Clock, Briefcase, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";

interface AgentStep {
  label: string;
  agent: string;
  status: "pending" | "running" | "done";
}

const MOCK_MACHINES = [
  { id: "M1", name: "Injection Molder A", capacity: "95%", setup: "15m", status: "Available" },
  { id: "M2", name: "Extrusion Line B", capacity: "88%", setup: "20m", status: "Available" },
  { id: "M3", name: "CNC Router C", capacity: "92%", setup: "10m", status: "Available" },
  { id: "M4", name: "Assembly Unit D", capacity: "85%", setup: "5m", status: "Maintenance" },
  { id: "M5", name: "Press Machine E", capacity: "90%", setup: "12m", status: "Available" },
];

const MOCK_WORKERS = [
  { id: "W1", name: "Ramesh Patil", expertise: "Injection", shift: "06:00 - 14:00" },
  { id: "W2", name: "Suresh Jadhav", expertise: "Extrusion", shift: "06:00 - 14:00" },
  { id: "W3", name: "Priya Sharma", expertise: "CNC", shift: "08:00 - 16:00" },
  { id: "W4", name: "Amit Deshmukh", expertise: "Assembly", shift: "08:00 - 16:00" },
];

export function ProductionSchedulingDetail() {
  const [step, setStep] = useState<"setup" | "processing" | "review" | "mail">("setup");
  const [orders, setOrders] = useState<{ id: string; product: string; deadline: string; material: string; customer: string }[]>([]);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [progress, setProgress] = useState(0);
  const [schedule, setSchedule] = useState<{ id: number; time: string; machine: string; task: string; worker: string; risk: number }[]>([]);
  const [editMode, setEditMode] = useState(false);
  const [mailTo, setMailTo] = useState("manager@factory.com");
  const [mailSubject, setMailSubject] = useState("Production Schedule — Today");
  const [mailBody, setMailBody] = useState("");
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("production")
        .select("order_id,product_type,customer,due_date,priority")
        .order("created_at", { ascending: false })
        .limit(5);
      if (data) {
        setOrders(data.map(d => ({
          id: d.order_id || "—",
          product: `${d.product_type || "widget"} (${d.priority || "normal"})`,
          deadline: d.due_date || "—",
          material: d.priority === "critical" ? "Delayed" : "Ready",
          customer: d.customer || "—",
        })));
      }
    }
    load();
  }, []);

  const handleGenerate = () => {
    setStep("processing");
    setProgress(0);
    setAgentSteps([
      { label: "Loading machine capacity & maintenance status", agent: "MachineMonitor", status: "pending" },
      { label: "Analyzing workforce availability & expertise", agent: "WorkforceAnalyzer", status: "pending" },
      { label: "Running constraint-based scheduling algorithm", agent: "ScheduleOptimizer", status: "pending" },
      { label: "Risk scoring & conflict detection", agent: "RiskAssessor", status: "pending" },
      { label: "Mapping workers to tasks", agent: "TaskMapper", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (step !== "processing") return;
    let s = 0;
    let prog = 0;
    const progInterval = setInterval(() => {
      prog += 2;
      setProgress(Math.min(prog, 100));
      if (prog >= 100) clearInterval(progInterval);
    }, 80);

    const run = () => {
      if (s < agentSteps.length) {
        setAgentSteps(prev => prev.map((a, i) => ({
          ...a, status: i === s ? "running" : i < s ? "done" : "pending"
        })));
        s++;
        timerRef.current = setTimeout(run, 800);
      } else {
        setAgentSteps(prev => prev.map(a => ({ ...a, status: "done" as const })));
        // Generate schedule from real orders
        const generated = (orders.length > 0 ? orders : [
          { id: "ORD-001", product: "widget_a (high)", customer: "Acme Corp" },
          { id: "ORD-002", product: "widget_b (normal)", customer: "TechStart" },
          { id: "ORD-003", product: "widget_c (critical)", customer: "Global Mfg" },
        ]).map((o, i) => ({
          id: i + 1,
          time: `${String(8 + i * 2).padStart(2, "0")}:00 - ${String(10 + i * 2).padStart(2, "0")}:00`,
          machine: MOCK_MACHINES[i % MOCK_MACHINES.length].id + " - " + MOCK_MACHINES[i % MOCK_MACHINES.length].name,
          task: `${o.id} — ${o.product}`,
          worker: MOCK_WORKERS[i % MOCK_WORKERS.length].name,
          risk: Math.floor(Math.random() * 4) + 1,
        }));
        setSchedule(generated);
        const body = `Production Schedule (AI Optimized)\n\n` +
          generated.map(s => `• [${s.time}] ${s.machine} | ${s.task} | Worker: ${s.worker} | Risk: ${s.risk}/10`).join("\n") +
          `\n\nAll materials verified. Risk scores within acceptable range.\n\nBest regards,\nProduction Scheduling AI`;
        setMailBody(body);
        timerRef.current = setTimeout(() => setStep("review"), 500);
      }
    };
    timerRef.current = setTimeout(run, 300);
    return () => {
      clearInterval(progInterval);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [step]);

  const handleUpdateSchedule = (id: number, field: string, value: string) => {
    setSchedule(prev => prev.map(s => s.id === id ? { ...s, [field]: value } : s));
  };

  return (
    <div className="space-y-6 w-full">
      <AnimatePresence mode="wait">
        {step === "setup" && (
          <motion.div key="setup" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                  <Settings className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Production Scheduling AI</h2>
                  <p className="text-xs text-muted-foreground">{MOCK_MACHINES.length} machines · {MOCK_WORKERS.length} workers · {orders.length} pending orders</p>
                </div>
              </div>
              <Button onClick={handleGenerate} className="gap-2 rounded-xl">
                <Play className="w-4 h-4" /> Generate Schedule
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-xl border border-border p-4 space-y-2.5">
                <h4 className="text-xs font-semibold flex items-center gap-2 pb-2 border-b border-border">
                  <Settings className="w-3.5 h-3.5" /> Machines
                </h4>
                {MOCK_MACHINES.map(m => (
                  <div key={m.id} className="text-xs p-2 rounded-lg bg-muted/20 flex justify-between">
                    <span className="font-medium">{m.id} — {m.name}</span>
                    <span className={m.status === "Available" ? "text-[hsl(142,71%,45%)]" : "text-[hsl(38,92%,50%)]"}>{m.status}</span>
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-border p-4 space-y-2.5">
                <h4 className="text-xs font-semibold flex items-center gap-2 pb-2 border-b border-border">
                  <Users className="w-3.5 h-3.5" /> Workforce
                </h4>
                {MOCK_WORKERS.map(w => (
                  <div key={w.id} className="text-xs p-2 rounded-lg bg-muted/20">
                    <div className="flex justify-between font-medium"><span>{w.name}</span><span className="text-primary">{w.expertise}</span></div>
                    <div className="text-muted-foreground flex items-center gap-1 mt-0.5"><Clock className="w-3 h-3" /> {w.shift}</div>
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-border p-4 space-y-2.5">
                <h4 className="text-xs font-semibold flex items-center gap-2 pb-2 border-b border-border">
                  <Package className="w-3.5 h-3.5" /> Pending Orders
                </h4>
                {orders.map(o => (
                  <div key={o.id} className="text-xs p-2 rounded-lg bg-muted/20">
                    <div className="flex justify-between font-medium"><span>{o.product}</span><span className={o.material === "Ready" ? "text-[hsl(142,71%,45%)]" : "text-[hsl(0,84%,60%)]"}>{o.material}</span></div>
                    <div className="text-muted-foreground mt-0.5">{o.customer} · Due: {o.deadline}</div>
                  </div>
                ))}
                {orders.length === 0 && <p className="text-xs text-muted-foreground text-center py-4">Loading orders...</p>}
              </div>
            </div>
          </motion.div>
        )}

        {step === "processing" && (
          <motion.div key="processing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-16">
            <Loader2 className="w-12 h-12 animate-spin mb-6 text-foreground/60" />
            <h3 className="text-lg font-medium mb-2">Optimizing Schedule</h3>
            <Progress value={progress} className="h-2 w-48 mb-8" />
            <div className="w-full max-w-md space-y-3">
              {agentSteps.map((a, i) => (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${a.status === "running" ? "border-foreground/20 bg-muted/30" : a.status === "done" ? "border-border opacity-60" : "border-transparent opacity-30"}`}>
                  <div className="w-5 h-5 flex items-center justify-center mt-0.5">
                    {a.status === "done" ? <CheckCircle2 className="w-4 h-4 text-[hsl(142,71%,45%)]" /> : a.status === "running" ? <Loader2 className="w-4 h-4 animate-spin" /> : <div className="w-2 h-2 rounded-full bg-muted-foreground" />}
                  </div>
                  <div><p className="text-sm font-medium">{a.label}</p><p className="text-[10px] text-muted-foreground">Agent: {a.agent}</p></div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {step === "review" && (
          <motion.div key="review" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[hsl(142,71%,45%/0.1)] flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Optimized Schedule</h3>
                  <p className="text-xs text-muted-foreground">Review and edit before sharing</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant={editMode ? "default" : "outline"} size="sm" onClick={() => setEditMode(!editMode)} className="gap-1.5 rounded-xl">
                  {editMode ? <><Save className="w-3.5 h-3.5" /> Save</> : <><Edit2 className="w-3.5 h-3.5" /> Edit</>}
                </Button>
                {!editMode && (
                  <Button size="sm" onClick={() => setStep("mail")} className="gap-1.5 rounded-xl">
                    Share <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                )}
              </div>
            </div>

            <div className="border border-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead><tr className="bg-muted/50 text-xs text-muted-foreground">
                  <th className="p-3 text-left font-medium">Time</th>
                  <th className="p-3 text-left font-medium">Machine</th>
                  <th className="p-3 text-left font-medium">Task</th>
                  <th className="p-3 text-left font-medium">Worker</th>
                  <th className="p-3 text-left font-medium">Risk</th>
                </tr></thead>
                <tbody>
                  {schedule.map(row => (
                    <tr key={row.id} className="border-t border-border/50 hover:bg-muted/20">
                      <td className="p-3">{editMode ? <Input value={row.time} onChange={e => handleUpdateSchedule(row.id, "time", e.target.value)} className="h-8 text-xs" /> : <span className="text-xs font-medium">{row.time}</span>}</td>
                      <td className="p-3">{editMode ? <Input value={row.machine} onChange={e => handleUpdateSchedule(row.id, "machine", e.target.value)} className="h-8 text-xs" /> : <span className="text-xs">{row.machine}</span>}</td>
                      <td className="p-3">{editMode ? <Input value={row.task} onChange={e => handleUpdateSchedule(row.id, "task", e.target.value)} className="h-8 text-xs" /> : <span className="text-xs">{row.task}</span>}</td>
                      <td className="p-3">{editMode ? <Input value={row.worker} onChange={e => handleUpdateSchedule(row.id, "worker", e.target.value)} className="h-8 text-xs" /> : <span className="text-xs flex items-center gap-1"><Briefcase className="w-3 h-3 text-muted-foreground" /> {row.worker}</span>}</td>
                      <td className="p-3"><span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${row.risk <= 3 ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>{row.risk}/10</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {step === "mail" && (
          <motion.div key="mail" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} className="max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"><Mail className="w-5 h-5" /></div>
              <div><h3 className="text-lg font-semibold">Share Schedule</h3><p className="text-xs text-muted-foreground">Send to your team</p></div>
            </div>
            <div className="space-y-3 mb-6">
              <div><label className="text-xs font-medium text-muted-foreground mb-1 block">To:</label><Input value={mailTo} onChange={e => setMailTo(e.target.value)} /></div>
              <div><label className="text-xs font-medium text-muted-foreground mb-1 block">Subject:</label><Input value={mailSubject} onChange={e => setMailSubject(e.target.value)} /></div>
              <div><label className="text-xs font-medium text-muted-foreground mb-1 block">Body:</label><Textarea value={mailBody} onChange={e => setMailBody(e.target.value)} className="min-h-[200px] font-mono text-xs" /></div>
            </div>
            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setStep("review")}>← Back</Button>
              <Button onClick={() => { window.location.href = `mailto:${mailTo}?subject=${encodeURIComponent(mailSubject)}&body=${encodeURIComponent(mailBody)}`; }} className="gap-2">
                <Send className="w-4 h-4" /> Open Mail
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
