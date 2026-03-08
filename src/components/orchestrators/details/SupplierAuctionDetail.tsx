import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Users, Timer, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface Bid { supplier: string; price: number; delivery: string; reliability: number; }

const initialBids: Bid[] = [
  { supplier: "PolyChem India", price: 185, delivery: "5 days", reliability: 96 },
  { supplier: "Apex Materials", price: 192, delivery: "3 days", reliability: 92 },
  { supplier: "GreenPoly Ltd", price: 178, delivery: "7 days", reliability: 88 },
  { supplier: "TechMat Corp", price: 195, delivery: "4 days", reliability: 94 },
];

export function SupplierAuctionDetail() {
  const [auctionActive, setAuctionActive] = useState(false);
  const [timer, setTimer] = useState(30);
  const [bids, setBids] = useState(initialBids);

  useEffect(() => {
    if (!auctionActive) return;
    const interval = setInterval(() => {
      setTimer(t => {
        if (t <= 1) { clearInterval(interval); setAuctionActive(false); return 0; }
        return t - 1;
      });
      setBids(prev => prev.map(b => ({
        ...b,
        price: Math.max(140, b.price - Math.floor(Math.random() * 5))
      })).sort((a, b) => a.price - b.price));
    }, 1000);
    return () => clearInterval(interval);
  }, [auctionActive]);

  const startAuction = () => { setAuctionActive(true); setTimer(30); setBids(initialBids); };

  const winner = !auctionActive && timer === 0 ? bids[0] : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          <span className="text-xs text-muted-foreground">{bids.length} suppliers competing</span>
        </div>
        <Button size="sm" onClick={startAuction} disabled={auctionActive} className="h-8 text-xs rounded-lg">
          {auctionActive ? <><Timer className="w-3 h-3 mr-1 animate-pulse" /> {timer}s remaining</> : "Start Auction"}
        </Button>
      </div>

      {winner && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="p-4 rounded-xl border border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)] flex items-center gap-3">
          <Trophy className="w-5 h-5 text-[hsl(38,92%,50%)]" />
          <div>
            <p className="text-sm font-semibold">{winner.supplier} wins at ₹{winner.price}/kg</p>
            <p className="text-xs text-muted-foreground">Delivery: {winner.delivery} · Reliability: {winner.reliability}%</p>
          </div>
        </motion.div>
      )}

      <div className="space-y-2">
        {bids.map((b, i) => (
          <motion.div key={b.supplier} layout className={`p-3 rounded-xl border ${i === 0 && auctionActive ? "border-[hsl(142,71%,45%/0.3)] bg-[hsl(142,71%,45%/0.03)]" : "border-border"} flex items-center gap-4`}>
            <span className="text-xs font-bold w-6">{i === 0 && auctionActive ? "🏆" : `#${i + 1}`}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{b.supplier}</p>
              <p className="text-[10px] text-muted-foreground">Delivery: {b.delivery} · Reliability: {b.reliability}%</p>
            </div>
            <div className="text-right">
              <p className={`text-lg font-bold ${i === 0 ? "text-[hsl(142,71%,45%)]" : ""}`}>₹{b.price}</p>
              <p className="text-[10px] text-muted-foreground">per kg</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
