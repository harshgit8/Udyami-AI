import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Clock, CheckCircle2, AlertTriangle, Settings, Users, Package, Mail, Edit2, Save, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";

// Initial Mock Data
const initialMachines = [
  { id: "M1", name: "Injection Molder A", capacity: 92, setupTime: "15m", status: "Available" },
  { id: "M2", name: "Extrusion Line B", capacity: 87, setupTime: "30m", status: "Available" },
  { id: "M3", name: "CNC Router C", capacity: 95, setupTime: "10m", status: "Available" },
  { id: "M4", name: "Assembly Unit D", capacity: 78, setupTime: "45m", status: "Maintenance" },
  { id: "M5", name: "Packaging Line E", capacity: 88, setupTime: "5m", status: "Available" },
];

const initialWorkers = [
  { id: "W1", name: "Alice S.", expertise: "Injection, CNC", shift: "Morning (06:00-14:00)" },
  { id: "W2", name: "Bob J.", expertise: "Assembly, Packaging", shift: "Morning (06:00-14:00)" },
  { id: "W3", name: "Charlie D.", expertise: "Extrusion", shift: "Morning (06:00-14:00)" },
  { id: "W4", name: "Diana P.", expertise: "CNC, Maintenance", shift: "Evening (14:00-22:00)" },
  { id: "W5", name: "Evan R.", expertise: "Packaging", shift: "Evening (14:00-22:00)" },
];

const initialOrders = [
  { id: "ORD-001", product: "Widget A", qty: 5000, deadline: "Today 18:00", material: "In Stock" },
  { id: "ORD-002", product: "Widget B", qty: 2500, deadline: "Tomorrow 12:00", material: "In Stock" },
  { id: "ORD-003", product: "Widget C", qty: 10000, deadline: "Today 22:00", material: "Low Stock" },
  { id: "ORD-004", product: "Widget D", qty: 1500, deadline: "Tomorrow 16:00", material: "In Stock" },
];

export function ProductionSchedulingDetail() {
  const [phase, setPhase] = useState<"input" | "processing" | "review" | "email">("input");
  const [progress, setProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState("");

  // States for inputs
  const [machines, setMachines] = useState(initialMachines);
  const [workers, setWorkers] = useState(initialWorkers);
  const [orders, setOrders] = useState(initialOrders);

  // Generated schedule state
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [schedule, setSchedule] = useState<any[]>([]);

  // Email states
  const [emailTo, setEmailTo] = useState("production.manager@company.com");
  const [emailSubject, setEmailSubject] = useState("Production Schedule - Today");
  const [emailBody, setEmailBody] = useState("");

  const handleGenerate = () => {
    setPhase("processing");
    setProgress(0);

    // Simulate real AI processing
    const steps = [
      { p: 15, msg: "Analyzing machine capacities and setup timings..." },
      { p: 35, msg: "Evaluating worker shifts and expertise matrices..." },
      { p: 55, msg: "Aligning order deadlines with material availability..." },
      { p: 80, msg: "Generating multi-variable integrated optimal schedule..." },
      { p: 100, msg: "Finalizing schedule mapping..." },
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        setProgress(steps[currentStep].p);
        setProcessingStatus(steps[currentStep].msg);
        currentStep++;
      } else {
        clearInterval(interval);
        setTimeout(() => {
          generateMockSchedule();
          setPhase("review");
        }, 500);
      }
    }, 1500); // 1.5 seconds per step for a realistic simulation feel
  };

  const generateMockSchedule = () => {
    // Generate a perfect mock schedule based on inputs
    const newSchedule = [
      { time: "06:00 - 10:00", m1: { task: "ORD-001 (Widget A)", worker: "Alice S." }, m2: { task: "ORD-003 (Widget C)", worker: "Charlie D." }, m3: { task: "ORD-002 (Widget B)", worker: "Diana P." }, m4: { task: "Maintenance", worker: "External" }, m5: { task: "ORD-001 Pack", worker: "Bob J." } },
      { time: "10:00 - 14:00", m1: { task: "ORD-001 (Widget A)", worker: "Alice S." }, m2: { task: "ORD-003 (Widget C)", worker: "Charlie D." }, m3: { task: "ORD-004 (Widget D)", worker: "Diana P." }, m4: { task: "Maintenance", worker: "External" }, m5: { task: "ORD-001 Pack", worker: "Bob J." } },
      { time: "14:00 - 18:00", m1: { task: "Setup / Idle", worker: "-" }, m2: { task: "ORD-003 (Widget C)", worker: "Alice S." }, m3: { task: "ORD-002 (Widget B)", worker: "Diana P." }, m4: { task: "ORD-004 Assembly", worker: "Bob J." }, m5: { task: "ORD-003 Pack", worker: "Evan R." } },
      { time: "18:00 - 22:00", m1: { task: "ORD-002 (Widget B)", worker: "Alice S." }, m2: { task: "Setup / Idle", worker: "-" }, m3: { task: "Idle", worker: "-" }, m4: { task: "ORD-004 Assembly", worker: "Bob J." }, m5: { task: "ORD-004 Pack", worker: "Evan R." } },
    ];
    setSchedule(newSchedule);

    const emailText = `Production Schedule for Today:

Orders Scheduled:
${orders.map(o => `- ${o.product}: ${o.qty} units (Due: ${o.deadline})`).join('\n')}

Machine Assignments:
- M1 (Injection): Alice S. (06:00-14:00)
- M2 (Extrusion): Charlie D. (06:00-14:00)
- M3 (CNC): Diana P. (06:00-18:00)
- M4 (Assembly): Bob J. (14:00-22:00)
- M5 (Packaging): Bob J. (06:00-14:00), Evan R. (14:00-22:00)

Please review and approve.
`;
    setEmailBody(emailText);
  };

  const updateScheduleCell = (rowIndex: number, colKey: string, field: 'task' | 'worker', value: string) => {
    const updated = [...schedule];
    updated[rowIndex][colKey as keyof typeof updated[0]][field] = value;
    setSchedule(updated);
  };

  return (
    <div className="space-y-6">
      {phase === "input" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Production Parameters</h3>
              <p className="text-sm text-muted-foreground">Configure inputs for AI scheduling optimizer.</p>
            </div>
            <Button onClick={handleGenerate} className="gap-2">
              <Settings className="w-4 h-4" />
              Generate Perfect Schedule
            </Button>
          </div>

          <Tabs defaultValue="machines" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="machines">Machines & Settings</TabsTrigger>
              <TabsTrigger value="workers">Workforce & Shifts</TabsTrigger>
              <TabsTrigger value="orders">Orders & Materials</TabsTrigger>
            </TabsList>

            <TabsContent value="machines" className="space-y-4 p-4 border rounded-lg mt-2">
              <div className="grid grid-cols-5 gap-4 font-medium text-sm text-muted-foreground pb-2 border-b">
                <div>Machine</div>
                <div>Capacity (%)</div>
                <div>Setup Time</div>
                <div>Status</div>
                <div>Action</div>
              </div>
              {machines.map((m, i) => (
                <div key={m.id} className="grid grid-cols-5 gap-4 items-center">
                  <div className="text-sm font-medium">{m.id} - {m.name}</div>
                  <Input type="number" value={m.capacity} onChange={(e) => {
                    const newM = [...machines]; newM[i].capacity = Number(e.target.value); setMachines(newM);
                  }} className="h-8" />
                  <Input value={m.setupTime} onChange={(e) => {
                    const newM = [...machines]; newM[i].setupTime = e.target.value; setMachines(newM);
                  }} className="h-8" />
                  <div className="text-sm">{m.status}</div>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Edit2 className="w-4 h-4" /></Button>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="workers" className="space-y-4 p-4 border rounded-lg mt-2">
              <div className="grid grid-cols-4 gap-4 font-medium text-sm text-muted-foreground pb-2 border-b">
                <div>Worker</div>
                <div>Expertise</div>
                <div>Shift</div>
                <div>Action</div>
              </div>
              {workers.map((w, i) => (
                <div key={w.id} className="grid grid-cols-4 gap-4 items-center">
                  <div className="text-sm font-medium">{w.name}</div>
                  <Input value={w.expertise} onChange={(e) => {
                    const newW = [...workers]; newW[i].expertise = e.target.value; setWorkers(newW);
                  }} className="h-8" />
                  <Input value={w.shift} onChange={(e) => {
                    const newW = [...workers]; newW[i].shift = e.target.value; setWorkers(newW);
                  }} className="h-8" />
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Edit2 className="w-4 h-4" /></Button>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="orders" className="space-y-4 p-4 border rounded-lg mt-2">
              <div className="grid grid-cols-5 gap-4 font-medium text-sm text-muted-foreground pb-2 border-b">
                <div>Order ID</div>
                <div>Product</div>
                <div>Qty</div>
                <div>Deadline</div>
                <div>Material</div>
              </div>
              {orders.map((o, i) => (
                <div key={o.id} className="grid grid-cols-5 gap-4 items-center">
                  <div className="text-sm font-medium">{o.id}</div>
                  <div className="text-sm">{o.product}</div>
                  <Input type="number" value={o.qty} onChange={(e) => {
                    const newO = [...orders]; newO[i].qty = Number(e.target.value); setOrders(newO);
                  }} className="h-8" />
                  <Input value={o.deadline} onChange={(e) => {
                    const newO = [...orders]; newO[i].deadline = e.target.value; setOrders(newO);
                  }} className="h-8" />
                  <div className={`text-xs px-2 py-1 rounded-full w-fit ${o.material === 'In Stock' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'}`}>
                    {o.material}
                  </div>
                </div>
              ))}
            </TabsContent>
          </Tabs>
        </motion.div>
      )}

      {phase === "processing" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center py-20 space-y-8">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 border-4 border-muted rounded-full"></div>
            <motion.div
              className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <Settings className="w-8 h-8 text-primary animate-pulse" />
            </div>
          </div>
          <div className="text-center space-y-2 w-full max-w-md">
            <h3 className="text-lg font-semibold text-foreground">AI Orchestrator Processing</h3>
            <p className="text-sm text-muted-foreground h-5">{processingStatus}</p>
            <Progress value={progress} className="h-2 w-full" />
          </div>
        </motion.div>
      )}

      {phase === "review" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Integrated Master Schedule
              </h3>
              <p className="text-sm text-muted-foreground">Review, edit, and manually override AI suggestions before finalization.</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setPhase("input")}>Edit Inputs</Button>
              <Button onClick={() => setPhase("email")} className="gap-2">
                <Mail className="w-4 h-4" />
                Approve & Send
              </Button>
            </div>
          </div>

          <div className="rounded-xl border border-border overflow-hidden overflow-x-auto">
            <table className="w-full text-xs min-w-[800px]">
              <thead>
                <tr className="bg-muted/50">
                  <th className="text-left p-3 font-medium text-muted-foreground w-32 border-b">Time Slot</th>
                  {["M1 (Injection)", "M2 (Extrusion)", "M3 (CNC)", "M4 (Assembly)", "M5 (Packaging)"].map((m) => (
                    <th key={m} className="text-left p-3 font-medium text-muted-foreground border-b border-l">{m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {schedule.map((row, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/20 transition-colors">
                    <td className="p-3 font-medium bg-muted/10">{row.time}</td>
                    {['m1', 'm2', 'm3', 'm4', 'm5'].map((mKey) => {
                      const colKey = mKey as keyof typeof row;
                      if (colKey === 'time') return null; // Shouldn't happen but typescript safety
                      const cell = row[colKey] as {task: string, worker: string};
                      return (
                      <td key={mKey} className="p-2 border-l">
                        <div className="space-y-1.5">
                          <Input
                            value={cell.task}
                            onChange={(e) => updateScheduleCell(i, mKey, 'task', e.target.value)}
                            className={`h-7 text-[10px] ${cell.task.includes('Idle') || cell.task.includes('Setup') || cell.task.includes('Maintenance') ? 'bg-muted/50 text-muted-foreground' : 'bg-[hsl(142,71%,45%/0.05)] border-[hsl(142,71%,45%/0.2)]'}`}
                          />
                          <div className="flex items-center gap-1">
                            <Users className="w-3 h-3 text-muted-foreground" />
                            <Input
                              value={cell.worker}
                              onChange={(e) => updateScheduleCell(i, mKey, 'worker', e.target.value)}
                              className="h-6 text-[10px] bg-transparent border-transparent hover:border-input focus:bg-background px-1"
                            />
                          </div>
                        </div>
                      </td>
                    )})}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Overall Utilization", value: "96%", sub: "AI optimized (+5%)" },
              { label: "Orders Met", value: "4/4", sub: "100% On-Time Delivery" },
              { label: "Workforce Allocation", value: "100%", sub: "No overlapping shifts" },
            ].map((s) => (
              <div key={s.label} className="p-4 rounded-xl border bg-card text-center shadow-sm">
                <p className="text-2xl font-semibold text-primary">{s.value}</p>
                <p className="text-xs font-medium text-muted-foreground mt-1">{s.label}</p>
                <p className="text-[10px] text-[hsl(142,71%,45%)] mt-1 font-medium">{s.sub}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {phase === "email" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4 max-w-2xl mx-auto border rounded-xl p-6 bg-card shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-primary/10 rounded-full">
              <Mail className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">Distribute Schedule</h3>
              <p className="text-sm text-muted-foreground">Send the finalized schedule to stakeholders.</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>To</Label>
              <Input value={emailTo} onChange={(e) => setEmailTo(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Subject</Label>
              <Input value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Message Body</Label>
              <Textarea
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                className="min-h-[250px] font-mono text-sm"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={() => setPhase("review")}>Back to Review</Button>
            <Button className="gap-2" onClick={() => {
              window.location.href = `mailto:${emailTo}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`;
            }}>
              <Send className="w-4 h-4" />
              Send Email
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
