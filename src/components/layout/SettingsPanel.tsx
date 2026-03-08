import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Settings, X, Zap, Moon, Volume2, Globe, Shield, RefreshCw } from "lucide-react";
import { Switch } from "@/components/ui/switch";

interface SettingToggle {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  defaultValue: boolean;
  accent?: boolean;
}

const settingsConfig: SettingToggle[] = [
  {
    id: "autopilot",
    label: "Autopilot Mode",
    description: "Let AI agents auto-execute tasks like quotations, scheduling & invoicing.",
    icon: Zap,
    defaultValue: true,
    accent: true,
  },
  {
    id: "dark_mode",
    label: "Dark Mode",
    description: "Switch to dark interface theme.",
    icon: Moon,
    defaultValue: false,
  },
  {
    id: "sound",
    label: "Sound Alerts",
    description: "Play audio cues for critical events.",
    icon: Volume2,
    defaultValue: true,
  },
  {
    id: "realtime",
    label: "Real-time Sync",
    description: "Live-sync data across all modules.",
    icon: RefreshCw,
    defaultValue: true,
  },
  {
    id: "language",
    label: "Multi-language",
    description: "Enable Hindi / regional language support.",
    icon: Globe,
    defaultValue: false,
  },
  {
    id: "security",
    label: "Enhanced Security",
    description: "Enable 2FA and audit logging.",
    icon: Shield,
    defaultValue: true,
  },
];

export function SettingsPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [values, setValues] = useState<Record<string, boolean>>(
    Object.fromEntries(settingsConfig.map((s) => [s.id, s.defaultValue]))
  );

  const toggle = (id: string) => setValues((prev) => ({ ...prev, [id]: !prev[id] }));

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
            className="absolute right-4 top-12 z-50 w-80 rounded-xl border border-border bg-card shadow-2xl"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-foreground" />
                <span className="text-sm font-semibold">Settings</span>
              </div>
              <button onClick={onClose} className="p-1 rounded-md hover:bg-muted transition-colors">
                <X className="w-3.5 h-3.5 text-muted-foreground" />
              </button>
            </div>

            <div className="max-h-[420px] overflow-y-auto">
              {settingsConfig.map((setting) => {
                const Icon = setting.icon;
                const isOn = values[setting.id];
                return (
                  <div
                    key={setting.id}
                    className={`flex items-start gap-3 px-4 py-3 border-b border-border/50 ${
                      setting.accent && isOn ? "bg-muted/40" : ""
                    }`}
                  >
                    <div className={`mt-0.5 p-1.5 rounded-lg shrink-0 ${isOn ? "bg-foreground/10" : "bg-muted"}`}>
                      <Icon className={`w-3.5 h-3.5 ${isOn ? "text-foreground" : "text-muted-foreground"}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium">{setting.label}</span>
                        {setting.accent && isOn && (
                          <span className="text-[9px] bg-foreground text-background px-1.5 py-0.5 rounded-full font-semibold uppercase tracking-wider">
                            Active
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">{setting.description}</p>
                    </div>
                    <Switch
                      checked={isOn}
                      onCheckedChange={() => toggle(setting.id)}
                      className="mt-1 shrink-0"
                    />
                  </div>
                );
              })}
            </div>

            <div className="px-4 py-2.5 border-t border-border flex items-center justify-between">
              <p className="text-[10px] text-muted-foreground">v2.1.0 • Udyami Cloud</p>
              <button className="text-[11px] text-muted-foreground hover:text-foreground transition-colors font-medium">
                Reset defaults
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
