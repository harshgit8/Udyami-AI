import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Receipt, Upload, FileText, CheckCircle2, Loader2, Save, Mail, Trash2, History, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";

interface InvoiceRecord {
  id: string;
  customer: string;
  product: string;
  amount: string;
  tax: string;
  status: string;
  date: string;
  rawData?: Record<string, unknown>;
}

interface AgentStep {
  label: string;
  agent: string;
  status: "pending" | "running" | "done";
}

export function InvoiceGenerationDetail() {
  const [viewState, setViewState] = useState<"prompts" | "processing" | "result" | "history">("prompts");
  const [invoices, setInvoices] = useState<InvoiceRecord[]>([]);
  const [activePrompt, setActivePrompt] = useState<string | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [savedDocs, setSavedDocs] = useState<InvoiceRecord[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<InvoiceRecord | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  // Load real invoices from DB
  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("invoiceresult")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(6);
      if (data) {
        setInvoices(data.map(d => ({
          id: d.invoice_number || `INV-${d.id}`,
          customer: d.customer_name || "—",
          product: d.product || "—",
          amount: `₹${Number(d.grand_total || 0).toLocaleString("en-IN")}`,
          tax: `₹${Number(d.total_tax || 0).toLocaleString("en-IN")}`,
          status: (d.balance_due && Number(d.balance_due) > 0) ? "due" : "paid",
          date: d.invoice_date || "—",
          rawData: d as unknown as Record<string, unknown>,
        })));
      }
    }
    load();
    // Load saved session docs
    const stored = sessionStorage.getItem("udyami-saved-invoices");
    if (stored) setSavedDocs(JSON.parse(stored));
  }, []);

  const prompts = [
    "Generate GST invoice for Quantum Materials — Junction Box Cover order",
    "Create invoice for PowerCable Co — LED Light Fixture Cover (1000 units)",
    "Draft tax invoice for Apex Plastics — Wire Harness Insulation batch",
  ];

  const handlePromptClick = (prompt: string) => {
    setActivePrompt(prompt);
    setViewState("processing");
    setAgentSteps([
      { label: "Fetching order & customer data from CRM", agent: "DataGatherer", status: "pending" },
      { label: "Validating GST compliance & tax calculation", agent: "ComplianceEngine", status: "pending" },
      { label: "Cross-referencing quality inspection clearance", agent: "QualityGate", status: "pending" },
      { label: "Generating invoice document layout", agent: "DocumentCrafter", status: "pending" },
    ]);
  };

  useEffect(() => {
    if (viewState !== "processing") return;
    let step = 0;
    const run = () => {
      if (step < agentSteps.length) {
        setAgentSteps(prev => prev.map((s, i) => ({
          ...s,
          status: i === step ? "running" : i < step ? "done" : "pending"
        })));
        step++;
        timerRef.current = setTimeout(run, 1200);
      } else {
        setAgentSteps(prev => prev.map(s => ({ ...s, status: "done" as const })));
        timerRef.current = setTimeout(() => setViewState("result"), 600);
      }
    };
    timerRef.current = setTimeout(run, 400);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [viewState]);

  const mockInvoice = {
    number: "INV-2026-03-13-" + Math.floor(100000 + Math.random() * 900000),
    customer: activePrompt?.includes("Quantum") ? "Quantum Materials" : activePrompt?.includes("PowerCable") ? "PowerCable Co" : "Apex Plastics",
    gstin: activePrompt?.includes("Quantum") ? "33AABQM7890P1Z5" : activePrompt?.includes("PowerCable") ? "08AABPC1234L1Z0" : "24AABAP3456O1Z1",
    product: activePrompt?.includes("Junction") ? "Junction Box Cover PC/ABS" : activePrompt?.includes("LED") ? "LED Light Fixture Cover PMMA" : "Wire Harness Insulation TPE",
    qty: activePrompt?.includes("LED") ? 1000 : activePrompt?.includes("Junction") ? 75 : 150,
    subtotal: activePrompt?.includes("LED") ? 373000 : activePrompt?.includes("Junction") ? 34800 : 66000,
    taxType: "IGST",
    taxRate: 18,
    get taxAmount() { return Math.round(this.subtotal * this.taxRate / 100); },
    get grandTotal() { return this.subtotal + this.taxAmount; },
    date: new Date().toISOString().slice(0, 10),
    poNumber: `PO/${activePrompt?.includes("Quantum") ? "QM" : activePrompt?.includes("PowerCable") ? "PC" : "AP"}/2026/${String(Math.floor(100 + Math.random() * 900)).padStart(4, "0")}`,
  };

  const handleAction = (action: "save" | "email" | "discard") => {
    if (action === "save") {
      const doc: InvoiceRecord = {
        id: mockInvoice.number,
        customer: mockInvoice.customer,
        product: mockInvoice.product,
        amount: `₹${mockInvoice.grandTotal.toLocaleString("en-IN")}`,
        tax: `₹${mockInvoice.taxAmount.toLocaleString("en-IN")}`,
        status: "saved",
        date: mockInvoice.date,
      };
      const updated = [doc, ...savedDocs].slice(0, 4);
      setSavedDocs(updated);
      sessionStorage.setItem("udyami-saved-invoices", JSON.stringify(updated));
    }
    setViewState("prompts");
    setActivePrompt(null);
  };

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "prompts" && (
          <motion.div key="prompts" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                  <Receipt className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Invoice Generation AI</h2>
                  <p className="text-xs text-muted-foreground">GST-compliant invoices • Auto tax calculation • {invoices.length} invoices in database</p>
                </div>
              </div>
              <div className="flex gap-2">
                {savedDocs.length > 0 && (
                  <Button variant="outline" size="sm" className="h-9 rounded-xl gap-1.5" onClick={() => setViewState("history")}>
                    <History className="w-3.5 h-3.5" /> Saved ({savedDocs.length})
                  </Button>
                )}
              </div>
            </div>

            <div className="space-y-2.5 mb-8">
              {prompts.map((prompt, i) => (
                <button key={i} onClick={() => handlePromptClick(prompt)}
                  className="w-full text-left p-4 rounded-xl border border-border bg-background hover:bg-muted/30 hover:border-foreground/10 transition-all text-sm">
                  {prompt}
                </button>
              ))}
            </div>

            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Recent Invoices from Database
            </h3>
            <div className="rounded-xl border border-border overflow-hidden">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-muted/50">
                    {["Invoice #", "Customer", "Product", "Amount", "Tax", "Status", "Date"].map(h => (
                      <th key={h} className="text-left p-3 font-medium text-muted-foreground">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {invoices.map(inv => (
                    <tr key={inv.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                      <td className="p-3 font-medium">{inv.id}</td>
                      <td className="p-3">{inv.customer}</td>
                      <td className="p-3 text-muted-foreground max-w-[120px] truncate">{inv.product}</td>
                      <td className="p-3 font-medium">{inv.amount}</td>
                      <td className="p-3 text-muted-foreground">{inv.tax}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${inv.status === "paid" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>
                          {inv.status}
                        </span>
                      </td>
                      <td className="p-3 text-muted-foreground">{inv.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {viewState === "processing" && (
          <motion.div key="processing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center py-16">
            <Loader2 className="w-12 h-12 animate-spin mb-6 text-foreground/60" />
            <h3 className="text-lg font-medium mb-8">Agents Processing Invoice</h3>
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
          <motion.div key="result" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[hsl(142,71%,45%/0.1)] flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-[hsl(142,71%,45%)]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Invoice Generated</h2>
                <p className="text-xs text-muted-foreground">{mockInvoice.number}</p>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-background mb-6">
              <div className="flex justify-between items-start mb-6 pb-4 border-b border-border">
                <div>
                  <h3 className="text-base font-bold">TAX INVOICE</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{mockInvoice.number}</p>
                  <p className="text-xs text-muted-foreground">Date: {mockInvoice.date}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold">Udyami Manufacturing</p>
                  <p className="text-[10px] text-muted-foreground">GSTIN: 27AADCU2230M1Z2</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-[10px] text-muted-foreground mb-1">Billed To:</p>
                  <p className="text-sm font-medium">{mockInvoice.customer}</p>
                  <p className="text-[10px] text-muted-foreground">GSTIN: {mockInvoice.gstin}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted-foreground mb-1">PO Number:</p>
                  <p className="text-sm font-medium">{mockInvoice.poNumber}</p>
                </div>
              </div>

              <table className="w-full text-sm mb-4">
                <thead>
                  <tr className="border-b border-border text-xs text-muted-foreground">
                    <th className="text-left py-2 font-medium">Description</th>
                    <th className="text-right py-2 font-medium">Qty</th>
                    <th className="text-right py-2 font-medium">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border/50">
                    <td className="py-2">{mockInvoice.product}</td>
                    <td className="py-2 text-right">{mockInvoice.qty}</td>
                    <td className="py-2 text-right">₹{mockInvoice.subtotal.toLocaleString("en-IN")}</td>
                  </tr>
                  <tr className="text-muted-foreground text-xs">
                    <td className="py-1.5" colSpan={2}>{mockInvoice.taxType} ({mockInvoice.taxRate}%)</td>
                    <td className="py-1.5 text-right">₹{mockInvoice.taxAmount.toLocaleString("en-IN")}</td>
                  </tr>
                  <tr className="font-bold border-t border-border">
                    <td className="py-3" colSpan={2}>Grand Total</td>
                    <td className="py-3 text-right text-base">₹{mockInvoice.grandTotal.toLocaleString("en-IN")}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="flex gap-3">
              <Button onClick={() => handleAction("save")} className="flex-1 h-11 rounded-xl gap-2">
                <Save className="w-4 h-4" /> Save Invoice
              </Button>
              <Button onClick={() => handleAction("email")} variant="secondary" className="flex-1 h-11 rounded-xl gap-2">
                <Mail className="w-4 h-4" /> Email Invoice
              </Button>
              <Button onClick={() => handleAction("discard")} variant="ghost" className="h-11 px-4 rounded-xl text-destructive hover:text-destructive">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}

        {viewState === "history" && (
          <motion.div key="history" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <History className="w-5 h-5" /> Saved Invoices
              </h2>
              <Button variant="ghost" size="sm" onClick={() => { setViewState("prompts"); setSelectedDoc(null); }}>← Back</Button>
            </div>
            {selectedDoc ? (
              <div className="p-6 rounded-xl border border-border bg-background">
                <h3 className="font-bold mb-2">{selectedDoc.id}</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-muted-foreground">Customer:</span> {selectedDoc.customer}</div>
                  <div><span className="text-muted-foreground">Product:</span> {selectedDoc.product}</div>
                  <div><span className="text-muted-foreground">Amount:</span> {selectedDoc.amount}</div>
                  <div><span className="text-muted-foreground">Tax:</span> {selectedDoc.tax}</div>
                  <div><span className="text-muted-foreground">Date:</span> {selectedDoc.date}</div>
                </div>
                <Button variant="ghost" size="sm" className="mt-4" onClick={() => setSelectedDoc(null)}>← Back to list</Button>
              </div>
            ) : (
              <div className="space-y-2">
                {savedDocs.map(doc => (
                  <button key={doc.id} onClick={() => setSelectedDoc(doc)}
                    className="w-full flex items-center justify-between p-4 rounded-xl border border-border bg-background hover:bg-muted/30 transition-colors">
                    <div className="text-left">
                      <p className="text-sm font-medium">{doc.id}</p>
                      <p className="text-xs text-muted-foreground">{doc.customer} · {doc.product}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold">{doc.amount}</span>
                      <Eye className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </button>
                ))}
                {savedDocs.length === 0 && <p className="text-sm text-muted-foreground text-center py-8">No saved invoices yet. Generate one to get started.</p>}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
