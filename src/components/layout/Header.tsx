import { useState } from "react";
import { motion } from "framer-motion";
import { Bell, Search, Settings } from "lucide-react";
import { NotificationsPanel } from "./NotificationsPanel";
import { SettingsPanel } from "./SettingsPanel";

interface HeaderProps {
  title?: string;
}

export function Header({ title = "UDYAMI AI" }: HeaderProps) {
  const [notifOpen, setNotifOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-border bg-card/80 backdrop-blur-xl sticky top-0 z-40 relative"
    >
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-foreground flex items-center justify-center overflow-hidden">
            <img src="/logo.svg" alt="Udyami AI" className="w-6 h-6 invert" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-bold tracking-tight">{title}</h1>
            <span className="text-[10px] text-muted-foreground tracking-wide">
              AI Operating System for Manufacturing
            </span>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-2">
          <div className="flex items-center gap-2 bg-muted rounded-lg px-3 py-1.5">
            <Search className="w-3.5 h-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search modules..."
              className="bg-transparent text-xs outline-none w-48 placeholder:text-muted-foreground"
            />
            <kbd className="text-[10px] text-muted-foreground bg-background rounded px-1.5 py-0.5">⌘K</kbd>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => { setNotifOpen(!notifOpen); setSettingsOpen(false); }}
            className={`relative p-2 rounded-lg transition-colors ${notifOpen ? "bg-muted" : "hover:bg-muted"}`}
          >
            <Bell className="w-4 h-4 text-muted-foreground" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-foreground" />
          </button>
          <button
            onClick={() => { setSettingsOpen(!settingsOpen); setNotifOpen(false); }}
            className={`p-2 rounded-lg transition-colors ${settingsOpen ? "bg-muted" : "hover:bg-muted"}`}
          >
            <Settings className={`w-4 h-4 text-muted-foreground transition-transform duration-300 ${settingsOpen ? "rotate-90" : ""}`} />
          </button>
          <div className="w-8 h-8 rounded-full bg-foreground text-background flex items-center justify-center text-xs font-medium">
            OP
          </div>
        </div>
      </div>

      <NotificationsPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
      <SettingsPanel open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </motion.header>
  );
}
