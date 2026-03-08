import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Download, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const recentQuotes = [
  { id: "QT-2026-047", customer: "Techno Mfg", product: "Widget A", qty: 500, total: "₹3,45,000", status: "sent", date: "Today" },
  { id: "QT-2026-046", customer: "Apex Industries", product: "Widget C", qty: 1200, total: "₹8,94,000", status: "accepted", date: "Yesterday" },
  { id: "QT-2026-045", customer: "Global Parts", product: "Widget B", qty: 300, total: "₹2,10,000", status: "pending", date: "2 days ago" },
  { id: "QT-2026-044", customer: "Prime Corp", product: "Widget D", qty: 800, total: "₹5,60,000", status: "accepted", date: "3 days ago" },
];

export function QuotationGeneratorDetail() {
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => { setGenerating(false); setGenerated(true); }, 2500);
  };

  return (
    <div className="space-y-6">
      {/* Quick Generate */}
      <div className="p-4 rounded-xl border border-border bg-muted/30">
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Quick Generate</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Customer</label>
            <Input placeholder="Customer name" className="h-9 text-sm rounded-lg" defaultValue="Techno Mfg" />
          </div>
          <div>
            <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Product</label>
            <Select defaultValue="widget_a">
              <SelectTrigger className="h-9 text-sm rounded-lg"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="widget_a">Widget A</SelectItem>
                <SelectItem value="widget_b">Widget B</SelectItem>
                <SelectItem value="widget_c">Widget C</SelectItem>
                <SelectItem value="widget_d">Widget D</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-[10px] font-medium text-muted-foreground mb-1 block">Quantity</label>
            <Input type="number" placeholder="Units" className="h-9 text-sm rounded-lg" defaultValue="500" />
          </div>
          <div className="flex items-end">
            <Button onClick={handleGenerate} disabled={generating} className="w-full h-9 text-xs rounded-lg">
              {generating ? "Generating…" : generated ? <><CheckCircle2 className="w-3 h-3 mr-1" /> Generated</> : <><Sparkles className="w-3 h-3 mr-1" /> Generate</>}
            </Button>
          </div>
        </div>
      </div>

      {/* Generated Quote Preview */}
      {generated && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-5 rounded-xl border border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold">Quote QT-2026-048</p>
              <p className="text-xs text-muted-foreground">Techno Mfg · Widget A · 500 units</p>
            </div>
            <Button variant="outline" size="sm" className="h-8 text-xs rounded-lg"><Download className="w-3 h-3 mr-1" /> Export PDF</Button>
          </div>
          <div className="grid grid-cols-4 gap-4 text-center">
            {[
              { label: "Material Cost", value: "₹1,25,000" },
              { label: "Production Cost", value: "₹87,500" },
              { label: "Profit Margin", value: "18.5%" },
              { label: "Grand Total", value: "₹3,52,400" },
            ].map(item => (
              <div key={item.label} className="p-2 rounded-lg bg-background">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="text-sm font-semibold mt-0.5">{item.value}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Recent Quotes */}
      <div>
        <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">Recent Quotations</h4>
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full text-xs">
            <thead><tr className="bg-muted/50">
              {["Quote ID", "Customer", "Product", "Qty", "Total", "Status", "Date"].map(h => <th key={h} className="text-left p-2.5 font-medium text-muted-foreground">{h}</th>)}
            </tr></thead>
            <tbody>
              {recentQuotes.map((q, i) => (
                <motion.tr key={q.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="border-t border-border hover:bg-muted/30 transition-colors">
                  <td className="p-2.5 font-medium">{q.id}</td>
                  <td className="p-2.5">{q.customer}</td>
                  <td className="p-2.5">{q.product}</td>
                  <td className="p-2.5">{q.qty}</td>
                  <td className="p-2.5 font-medium">{q.total}</td>
                  <td className="p-2.5">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${q.status === "accepted" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : q.status === "sent" ? "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]" : "bg-muted text-muted-foreground"}`}>{q.status}</span>
                  </td>
                  <td className="p-2.5 text-muted-foreground">{q.date}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
