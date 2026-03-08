import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, CheckCircle2, IndianRupee } from "lucide-react";
import { Button } from "@/components/ui/button";

const invoices = [
  { id: "INV-2026-089", customer: "Techno Mfg", amount: "₹3,45,000", tax: "₹62,100", status: "paid", date: "Mar 05" },
  { id: "INV-2026-088", customer: "Apex Industries", amount: "₹8,94,000", tax: "₹1,60,920", status: "overdue", date: "Mar 02" },
  { id: "INV-2026-087", customer: "Global Parts", amount: "₹2,10,000", tax: "₹37,800", status: "paid", date: "Feb 28" },
  { id: "INV-2026-086", customer: "Prime Corp", amount: "₹5,60,000", tax: "₹1,00,800", status: "pending", date: "Feb 25" },
  { id: "INV-2026-085", customer: "Metro Engg", amount: "₹4,20,000", tax: "₹75,600", status: "paid", date: "Feb 22" },
];

export function InvoiceGenerationDetail() {
  const [creating, setCreating] = useState(false);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Total Invoiced", value: "₹24.3L", sub: "This month" },
          { label: "Collected", value: "₹18.7L", sub: "77% collected" },
          { label: "Outstanding", value: "₹5.6L", sub: "3 pending" },
          { label: "Tax Filed", value: "₹4.37L", sub: "GST compliant" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className="text-lg font-semibold">{s.value}</p>
            <p className="text-[10px] font-medium text-muted-foreground">{s.label}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{s.sub}</p>
          </motion.div>
        ))}
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Recent Invoices</h4>
          <Button size="sm" className="h-8 text-xs rounded-lg" onClick={() => { setCreating(true); setTimeout(() => setCreating(false), 1500); }}>
            {creating ? "Creating…" : <><FileText className="w-3 h-3 mr-1" /> New Invoice</>}
          </Button>
        </div>
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full text-xs">
            <thead><tr className="bg-muted/50">
              {["Invoice", "Customer", "Amount", "Tax", "Status", "Date"].map(h => <th key={h} className="text-left p-2.5 font-medium text-muted-foreground">{h}</th>)}
            </tr></thead>
            <tbody>
              {invoices.map((inv, i) => (
                <motion.tr key={inv.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="border-t border-border hover:bg-muted/30 transition-colors">
                  <td className="p-2.5 font-medium">{inv.id}</td>
                  <td className="p-2.5">{inv.customer}</td>
                  <td className="p-2.5 font-medium">{inv.amount}</td>
                  <td className="p-2.5 text-muted-foreground">{inv.tax}</td>
                  <td className="p-2.5">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${inv.status === "paid" ? "bg-[hsl(142,71%,45%/0.1)] text-[hsl(142,71%,45%)]" : inv.status === "overdue" ? "bg-[hsl(0,84%,60%/0.1)] text-[hsl(0,84%,60%)]" : "bg-[hsl(38,92%,50%/0.1)] text-[hsl(38,92%,50%)]"}`}>{inv.status}</span>
                  </td>
                  <td className="p-2.5 text-muted-foreground">{inv.date}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
