import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, CheckCircle2, Loader2, Save, Download, History, Eye, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";

interface QuoteRecord {
  id: string;
  customer: string;
  product: string;
  qty: number;
  total: string;
  margin: string;
  status: string;
  date: string;
}

interface AgentStep {
  label: string;
  agent: string;
  status: "pending" | "running" | "done";
}

export function QuotationGeneratorDetail() {
  const [viewState, setViewState] = useState<"prompts" | "processing" | "result" | "history">("prompts");
  const [quotes, setQuotes] = useState<QuoteRecord[]>([]);
  const [activePrompt, setActivePrompt] = useState<string | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [savedDocs, setSavedDocs] = useState<QuoteRecord[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<QuoteRecord | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("quotationresult")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(6);
      if (data) {
        setQuotes(data.map(d => ({
          id: d.quote_id || `QT-${d.id}`,
          customer: d.customer || "—",
          product: d.product || "—",
          qty: d.quantity || 0,
          total: `₹${Number(d.grand_total || 0).toLocaleString("en-IN")}`,
          margin: `${d.profit_margin || 0}%`,
          status: "sent",
          date: d.valid_until || "—",
        })));
      }
    }
    load();
    const stored = sessionStorage.getItem("udyami-saved-quotes");
    if (stored) setSavedDocs(JSON.parse(stored));
  }, []);

  const prompts = [
    "Generate quotation for Acme Corp — 500 units widget_a with priority delivery",
    "Create quote for PowerCable Co — 300 units widget_e, 50% advance terms",
    "Draft pricing for FastTrack Ltd — 200 units widget_c, competitive bid",
  ];

  const handlePromptClick = (prompt: string) => {
    setActivePrompt(prompt);
    setViewState("processing");
    setAgentSteps([
      { label: "Analyzing material cost & current inventory", agent: "CostAnalyzer", status: "pending" },
      { label: "Calculating production capacity & lead time", agent: "CapacityPlanner", status: "pending" },
      { label: "Running competitive pricing analysis", agent: "PricingEngine", status: "pending" },
      { label: "Generating quotation document", agent: "DocumentCrafter", status: "pending" },
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
        timerRef.current = setTimeout(run, 1100);
      } else {
        setAgentSteps(prev => prev.map(s => ({ ...s, status: "done" as const })));
        timerRef.current = setTimeout(() => setViewState("result"), 500);
      }
    };
    timerRef.current = setTimeout(run, 300);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [viewState]);

  const mockQuote = {
    id: `QT-2026-${String(Math.floor(100 + Math.random() * 900))}`,
    customer: activePrompt?.includes("Acme") ? "Acme Corp" : activePrompt?.includes("PowerCable") ? "PowerCable Co" : "FastTrack Ltd",
    product: activePrompt?.includes("widget_a") ? "Widget A (ABS Compound)" : activePrompt?.includes("widget_e") ? "Widget E (PVC K70)" : "Widget C (PP-Talc)",
    qty: activePrompt?.includes("500") ? 500 : activePrompt?.includes("300") ? 300 : 200,
    materialCost: activePrompt?.includes("500") ? 58498 : activePrompt?.includes("300") ? 50321 : 29411,
    productionCost: activePrompt?.includes("500") ? 44520 : activePrompt?.includes("300") ? 26208 : 15092,
    qualityCost: 2500,
    profitMargin: 25,
    get subtotal() { return this.materialCost + this.productionCost + this.qualityCost; },
    get profitAmount() { return Math.round(this.subtotal * this.profitMargin / 100); },
    get totalBeforeTax() { return this.subtotal + this.profitAmount; },
    get gst() { return Math.round(this.totalBeforeTax * 0.18); },
    get grandTotal() { return this.totalBeforeTax + this.gst; },
    get unitPrice() { return Math.round(this.grandTotal / this.qty * 100) / 100; },
    leadTime: 9,
    paymentTerms: "50% advance, 50% on delivery",
    validUntil: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
  };

  const handleAction = (action: "save" | "discard") => {
    if (action === "save") {
      const doc: QuoteRecord = {
        id: mockQuote.id,
        customer: mockQuote.customer,
        product: mockQuote.product,
        qty: mockQuote.qty,
        total: `₹${mockQuote.grandTotal.toLocaleString("en-IN")}`,
        margin: `${mockQuote.profitMargin}%`,
        status: "saved",
        date: new Date().toISOString().slice(0, 10),
      };
      const updated = [doc, ...savedDocs].slice(0, 4);
      setSavedDocs(updated);
      sessionStorage.setItem("udyami-saved-quotes", JSON.stringify(updated));
    }
    setViewState("prompts");
    setActivePrompt(null);
  };

  return (
    <div className="space-y-6 pb-4">
      <AnimatePresence mode="wait">
        {viewState === "prompts" && (
          <motion.div key="prompts" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-muted/50 flex items-center justify-center">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Quotation Generator AI</h2>
                  <p className="text-xs text-muted-foreground">Cost-optimized quotes • {quotes.length} quotations in database</p>
                </div>
              </div>
              {savedDocs.length > 0 && (
                <Button variant="outline" size="sm" className="h-9 rounded-xl gap-1.5" onClick={() => setViewState("history")}>
                  <History className="w-3.5 h-3.5" /> Saved ({savedDocs.length})
                </Button>
              )}
            </div>

            <div className="space-y-2.5 mb-8">
              {prompts.map((prompt, i) => (
                <button key={i} onClick={() => handlePromptClick(prompt)}
                  className="w-full text-left p-4 rounded-xl border border-border bg-background hover:bg-muted/30 hover:border-foreground/10 transition-all text-sm">
                  {prompt}
                </button>
              ))}
            </div>

            <h3 className="text-sm font-semibold mb-3">Recent Quotations from Database</h3>
            <div className="rounded-xl border border-border overflow-hidden">
              <table className="w-full text-xs">
                <thead><tr className="bg-muted/50">
                  {["Quote ID", "Customer", "Product", "Qty", "Total", "Margin", "Valid Until"].map(h => (
                    <th key={h} className="text-left p-3 font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr></thead>
                <tbody>
                  {quotes.map(q => (
                    <tr key={q.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                      <td className="p-3 font-medium">{q.id}</td>
                      <td className="p-3">{q.customer}</td>
                      <td className="p-3 text-muted-foreground">{q.product}</td>
                      <td className="p-3">{q.qty}</td>
                      <td className="p-3 font-medium">{q.total}</td>
                      <td className="p-3"><span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]">{q.margin}</span></td>
                      <td className="p-3 text-muted-foreground">{q.date}</td>
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
            <h3 className="text-lg font-medium mb-8">Agents Generating Quotation</h3>
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
                <h2 className="text-lg font-semibold">Quotation Generated</h2>
                <p className="text-xs text-muted-foreground">{mockQuote.id} · Valid until {mockQuote.validUntil}</p>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-background mb-6">
              <div className="flex justify-between mb-6 pb-4 border-b border-border">
                <div>
                  <h3 className="text-base font-bold">QUOTATION</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{mockQuote.id}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold">{mockQuote.customer}</p>
                  <p className="text-xs text-muted-foreground">{mockQuote.product} × {mockQuote.qty}</p>
                </div>
              </div>

              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between py-1.5"><span className="text-muted-foreground">Material Cost</span><span>₹{mockQuote.materialCost.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-1.5"><span className="text-muted-foreground">Production Cost</span><span>₹{mockQuote.productionCost.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-1.5"><span className="text-muted-foreground">Quality Cost</span><span>₹{mockQuote.qualityCost.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-1.5 border-t border-border/50"><span>Subtotal</span><span className="font-medium">₹{mockQuote.subtotal.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-1.5"><span className="text-muted-foreground">Profit ({mockQuote.profitMargin}%)</span><span>₹{mockQuote.profitAmount.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-1.5"><span className="text-muted-foreground">GST (18%)</span><span>₹{mockQuote.gst.toLocaleString("en-IN")}</span></div>
                <div className="flex justify-between py-3 border-t border-border font-bold text-base"><span>Grand Total</span><span>₹{mockQuote.grandTotal.toLocaleString("en-IN")}</span></div>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-3 border-t border-border">
                <div className="text-center p-2 rounded-lg bg-muted/30">
                  <p className="text-[10px] text-muted-foreground">Unit Price</p>
                  <p className="text-sm font-semibold">₹{mockQuote.unitPrice.toLocaleString("en-IN")}</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-muted/30">
                  <p className="text-[10px] text-muted-foreground">Lead Time</p>
                  <p className="text-sm font-semibold">{mockQuote.leadTime} days</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-muted/30">
                  <p className="text-[10px] text-muted-foreground">Payment</p>
                  <p className="text-[11px] font-medium">{mockQuote.paymentTerms}</p>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button onClick={() => handleAction("save")} className="flex-1 h-11 rounded-xl gap-2">
                <Save className="w-4 h-4" /> Save Quotation
              </Button>
              <Button onClick={() => handleAction("discard")} variant="ghost" className="h-11 px-4 rounded-xl text-destructive hover:text-destructive">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}

        {viewState === "history" && (
          <motion.div key="history" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold flex items-center gap-2"><History className="w-5 h-5" /> Saved Quotations</h2>
              <Button variant="ghost" size="sm" onClick={() => { setViewState("prompts"); setSelectedDoc(null); }}>← Back</Button>
            </div>
            {selectedDoc ? (
              <div className="p-6 rounded-xl border border-border bg-background">
                <h3 className="font-bold mb-3">{selectedDoc.id}</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-muted-foreground">Customer:</span> {selectedDoc.customer}</div>
                  <div><span className="text-muted-foreground">Product:</span> {selectedDoc.product}</div>
                  <div><span className="text-muted-foreground">Quantity:</span> {selectedDoc.qty}</div>
                  <div><span className="text-muted-foreground">Total:</span> {selectedDoc.total}</div>
                  <div><span className="text-muted-foreground">Margin:</span> {selectedDoc.margin}</div>
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
                      <p className="text-xs text-muted-foreground">{doc.customer} · {doc.product} × {doc.qty}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold">{doc.total}</span>
                      <Eye className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </button>
                ))}
                {savedDocs.length === 0 && <p className="text-sm text-muted-foreground text-center py-8">No saved quotations yet.</p>}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
