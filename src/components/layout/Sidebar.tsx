import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Receipt,
  ClipboardCheck,
  Factory,
  FlaskConical,
  BarChart3,
  Cpu,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const mainItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "chat", label: "Udyami Copilot", icon: MessageSquare },
  { id: "orchestrators", label: "AI Orchestrators", icon: Cpu },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
];

const moduleItems = [
  { id: "quotations", label: "Quotations", icon: FileText },
  { id: "invoices", label: "Invoices", icon: Receipt },
  { id: "quality", label: "Quality", icon: ClipboardCheck },
  { id: "production", label: "Production", icon: Factory },
  { id: "rnd", label: "R&D", icon: FlaskConical },
];

function SidebarContent({ activeTab, onTabChange, collapsed, showLabels }: { activeTab: string; onTabChange: (tab: string) => void; collapsed: boolean; showLabels: boolean }) {
  return (
    <div className="flex-1 py-4 px-2 space-y-6 overflow-hidden">
      <div>
        {showLabels && (
          <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground px-3 mb-2">Main</p>
        )}
        <div className="space-y-0.5">
          {mainItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center gap-3 rounded-lg transition-all duration-150 ${
                  collapsed && !showLabels ? "justify-center px-2 py-2.5" : "px-3 py-2.5"
                } text-sm ${
                  isActive ? "bg-foreground text-background font-medium" : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
                title={!showLabels ? item.label : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {showLabels && <span>{item.label}</span>}
              </button>
            );
          })}
        </div>
      </div>
      <div>
        {showLabels && (
          <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground px-3 mb-2">Modules</p>
        )}
        <div className="space-y-0.5">
          {moduleItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center gap-3 rounded-lg transition-all duration-150 ${
                  collapsed && !showLabels ? "justify-center px-2 py-2.5" : "px-3 py-2.5"
                } text-sm ${
                  isActive ? "bg-foreground text-background font-medium" : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
                title={!showLabels ? item.label : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {showLabels && <span>{item.label}</span>}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const isMobile = useIsMobile();

  const handleTabChange = (tab: string) => {
    onTabChange(tab);
    if (isMobile) setMobileOpen(false);
  };

  // Mobile: hamburger + slide-out drawer
  if (isMobile) {
    return (
      <>
        <button
          onClick={() => setMobileOpen(true)}
          className="fixed bottom-4 left-4 z-50 p-3 rounded-full bg-foreground text-background shadow-lg"
        >
          <Menu className="w-5 h-5" />
        </button>
        <AnimatePresence>
          {mobileOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/50"
                onClick={() => setMobileOpen(false)}
              />
              <motion.aside
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
                className="fixed left-0 top-0 z-50 w-[260px] h-full bg-sidebar border-r border-border flex flex-col"
              >
                <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-foreground flex items-center justify-center">
                      <img src="/logo.svg" alt="Udyami AI" className="w-5 h-5 invert" />
                    </div>
                    <span className="text-sm font-bold">UDYAMI AI</span>
                  </div>
                  <button onClick={() => setMobileOpen(false)} className="p-1.5 rounded-lg hover:bg-muted">
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <SidebarContent activeTab={activeTab} onTabChange={handleTabChange} collapsed={false} showLabels={true} />
              </motion.aside>
            </>
          )}
        </AnimatePresence>
      </>
    );
  }

  // Desktop/Tablet
  return (
    <motion.aside
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0, width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.2 }}
      className="border-r border-border bg-sidebar h-[calc(100vh-49px)] sticky top-[49px] flex flex-col overflow-hidden"
    >
      <SidebarContent activeTab={activeTab} onTabChange={onTabChange} collapsed={collapsed} showLabels={!collapsed} />
      <div className="p-2 border-t border-sidebar-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs text-muted-foreground hover:bg-sidebar-accent transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </motion.aside>
  );
}
