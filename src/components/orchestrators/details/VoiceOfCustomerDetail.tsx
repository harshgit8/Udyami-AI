import { motion } from "framer-motion";
import { MessageCircle, ThumbsUp, ThumbsDown, Minus } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const reviews = [
  { customer: "Techno Mfg", product: "Widget A", sentiment: "positive", score: 4.5, feedback: "Excellent surface finish, consistent dimensions across batch." },
  { customer: "Apex Industries", product: "Widget C", sentiment: "negative", score: 2.1, feedback: "Color inconsistency in last shipment. 3 units had visible marks." },
  { customer: "Global Parts", product: "Widget B", sentiment: "positive", score: 4.8, feedback: "Best batch quality we've received. Zero defects." },
  { customer: "Prime Corp", product: "Widget D", sentiment: "neutral", score: 3.2, feedback: "Meets specs but delivery was 2 days late." },
  { customer: "Metro Engg", product: "Widget A", sentiment: "positive", score: 4.3, feedback: "Good quality. Packaging could be improved." },
];

export function VoiceOfCustomerDetail() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Avg Sentiment", value: "4.2/5", icon: ThumbsUp, color: "text-[hsl(142,71%,45%)]" },
          { label: "Positive Reviews", value: "72%", icon: ThumbsUp, color: "text-[hsl(142,71%,45%)]" },
          { label: "Complaints", value: "8", icon: ThumbsDown, color: "text-[hsl(0,84%,60%)]" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="p-3 rounded-xl bg-muted/50 text-center">
            <p className={`text-lg font-semibold ${s.color}`}>{s.value}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="space-y-2">
        {reviews.map((r, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="p-3 rounded-xl border border-border hover:bg-muted/30 transition-colors">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                {r.sentiment === "positive" ? <ThumbsUp className="w-3 h-3 text-[hsl(142,71%,45%)]" /> : r.sentiment === "negative" ? <ThumbsDown className="w-3 h-3 text-[hsl(0,84%,60%)]" /> : <Minus className="w-3 h-3 text-muted-foreground" />}
                <span className="text-xs font-medium">{r.customer}</span>
                <span className="text-[10px] text-muted-foreground">· {r.product}</span>
              </div>
              <span className="text-xs font-semibold">{r.score}/5</span>
            </div>
            <p className="text-xs text-muted-foreground">{r.feedback}</p>
          </motion.div>
        ))}
      </div>

      <div className="p-4 rounded-xl border border-border">
        <h4 className="text-xs font-medium mb-2">AI Improvement Suggestions</h4>
        <ul className="space-y-1.5 text-xs text-muted-foreground">
          <li>• <strong>Color consistency</strong>: Calibrate pigment dosing on Extrusion Line B</li>
          <li>• <strong>Packaging</strong>: Switch to foam-lined boxes for Widget A</li>
          <li>• <strong>Delivery</strong>: Add 1-day buffer for Prime Corp orders</li>
        </ul>
      </div>
    </div>
  );
}
