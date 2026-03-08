import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, CheckCircle2, AlertTriangle, Info, X, Clock, Zap } from "lucide-react";

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: "success" | "warning" | "info" | "alert";
  read: boolean;
}

const initialNotifications: Notification[] = [
  {
    id: "1",
    title: "Production Schedule Optimized",
    message: "Machine M3 schedule updated — 12% efficiency gain detected.",
    time: "2 min ago",
    type: "success",
    read: false,
  },
  {
    id: "2",
    title: "Quality Alert — Batch BATCH042",
    message: "Defect rate 4.8% exceeds threshold. Review recommended.",
    time: "8 min ago",
    type: "warning",
    read: false,
  },
  {
    id: "3",
    title: "Invoice INV-2026-031 Generated",
    message: "₹2,84,500 invoice for Kaveri Industries auto-generated.",
    time: "15 min ago",
    type: "info",
    read: false,
  },
  {
    id: "4",
    title: "Supplier Bid Received",
    message: "New bid from PolyTech Supplies: ₹72/kg for PVC Compound.",
    time: "22 min ago",
    type: "alert",
    read: true,
  },
  {
    id: "5",
    title: "R&D Formulation Ready",
    message: "RND015 formulation passed UL94 V-2 compliance simulation.",
    time: "1 hr ago",
    type: "success",
    read: true,
  },
  {
    id: "6",
    title: "Autopilot Completed 3 Tasks",
    message: "Quotation QR012, QR018, QR024 auto-processed successfully.",
    time: "2 hr ago",
    type: "info",
    read: true,
  },
];

const typeConfig = {
  success: { icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10" },
  warning: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
  info: { icon: Info, color: "text-blue-500", bg: "bg-blue-500/10" },
  alert: { icon: Zap, color: "text-orange-500", bg: "bg-orange-500/10" },
};

export function NotificationsPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [notifications, setNotifications] = useState(initialNotifications);
  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllRead = () => setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  const dismiss = (id: string) => setNotifications((prev) => prev.filter((n) => n.id !== id));

  return (
    <AnimatePresence>
      {open && (
        <>
          <div className="fixed inset-0 z-50" onClick={onClose} />
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            className="absolute right-16 top-12 z-50 w-96 rounded-xl border border-border bg-card shadow-2xl"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-foreground" />
                <span className="text-sm font-semibold">Notifications</span>
                {unreadCount > 0 && (
                  <span className="text-[10px] bg-foreground text-background px-1.5 py-0.5 rounded-full font-medium">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button onClick={markAllRead} className="text-[11px] text-muted-foreground hover:text-foreground transition-colors">
                    Mark all read
                  </button>
                )}
                <button onClick={onClose} className="p-1 rounded-md hover:bg-muted transition-colors">
                  <X className="w-3.5 h-3.5 text-muted-foreground" />
                </button>
              </div>
            </div>

            <div className="max-h-[400px] overflow-y-auto">
              {notifications.map((n) => {
                const cfg = typeConfig[n.type];
                const Icon = cfg.icon;
                return (
                  <motion.div
                    key={n.id}
                    layout
                    exit={{ opacity: 0, x: 20 }}
                    className={`flex gap-3 px-4 py-3 border-b border-border/50 hover:bg-muted/50 transition-colors group ${!n.read ? "bg-muted/30" : ""}`}
                  >
                    <div className={`mt-0.5 p-1.5 rounded-lg ${cfg.bg} shrink-0`}>
                      <Icon className={`w-3.5 h-3.5 ${cfg.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p className={`text-xs font-medium leading-tight ${!n.read ? "text-foreground" : "text-muted-foreground"}`}>
                          {n.title}
                        </p>
                        <button onClick={() => dismiss(n.id)} className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5">
                          <X className="w-3 h-3 text-muted-foreground" />
                        </button>
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">{n.message}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3 text-muted-foreground/60" />
                        <span className="text-[10px] text-muted-foreground/60">{n.time}</span>
                      </div>
                    </div>
                    {!n.read && <div className="w-1.5 h-1.5 rounded-full bg-foreground mt-2 shrink-0" />}
                  </motion.div>
                );
              })}
            </div>

            <div className="px-4 py-2.5 border-t border-border">
              <p className="text-[10px] text-muted-foreground text-center">All notifications from the last 24 hours</p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
