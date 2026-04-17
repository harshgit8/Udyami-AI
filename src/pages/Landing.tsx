import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowRight, FileText, Receipt, Factory, FlaskConical, ClipboardCheck, Sparkles, Lock, Database } from "lucide-react";
import { Button } from "@/components/ui/button";

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
};

const modules = [
  { icon: FileText, title: "Quotations", desc: "AI-assisted pricing with margin guardrails. GST-ready PDFs in one click." },
  { icon: Receipt, title: "Invoices", desc: "Sec 31 CGST-compliant invoices with HSN, CGST/SGST/IGST and balance tracking." },
  { icon: ClipboardCheck, title: "Quality", desc: "Inspection logs, defect rates, and disposition decisions tied to every batch." },
  { icon: Factory, title: "Production", desc: "Order scheduling with machine utilization, risk scoring and delay alerts." },
  { icon: FlaskConical, title: "R&D", desc: "Polymer formulation suggestions with UL94, RoHS, REACH compliance hints." },
];

const steps = [
  { n: "01", title: "We onboard your organization", body: "We create your workspace and issue logins for up to 4 team members. Zero IT setup on your side." },
  { n: "02", title: "Connect your data", body: "Sync from Google Sheets, CSV, or start fresh. Existing quotations, invoices and production data flow in." },
  { n: "03", title: "Run the day-to-day", body: "Generate quotes, raise invoices, log inspections, schedule production. All from one workspace." },
  { n: "04", title: "Let AI assist on demand", body: "Ask Udyami AI for pricing recommendations, formulation hints, or analytics only when you need it." },
];

export default function Landing() {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 80]);
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0.2]);

  useEffect(() => {
    document.title = "Udyami - Operating system for Indian polymer MSMEs";
    const meta = document.querySelector('meta[name="description"]');
    const content = "Udyami is the all-in-one operations suite for Indian polymer manufacturers. Quotations, invoices, quality, production and R&D with AI assistance built in.";
    if (meta) meta.setAttribute("content", content);
    else {
      const m = document.createElement("meta");
      m.name = "description"; m.content = content;
      document.head.appendChild(m);
    }
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* NAV */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-background/70 border-b border-border/40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="font-semibold tracking-tight text-lg">Udyami</Link>
          <nav className="flex items-center gap-2 sm:gap-4">
            <a href="#modules" className="hidden sm:inline text-sm text-muted-foreground hover:text-foreground transition-colors">Modules</a>
            <a href="#how" className="hidden sm:inline text-sm text-muted-foreground hover:text-foreground transition-colors">How it works</a>
            <a href="#trust" className="hidden sm:inline text-sm text-muted-foreground hover:text-foreground transition-colors">Trust</a>
            <Link to="/request-demo">
              <Button variant="ghost" size="sm">Request demo</Button>
            </Link>
            <Link to="/login">
              <Button size="sm">Login</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* HERO */}
      <section ref={heroRef} className="relative overflow-hidden">
        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-24 sm:pt-24 sm:pb-32 lg:pt-32 lg:pb-40">
          <motion.p {...fadeUp} className="text-sm tracking-widest uppercase text-muted-foreground mb-6">For Indian polymer MSMEs</motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="text-3xl sm:text-5xl lg:text-7xl font-semibold tracking-tight leading-[1.05] max-w-4xl"
          >
            The operating system for your manufacturing floor.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6 sm:mt-8 text-base sm:text-lg lg:text-xl text-muted-foreground max-w-2xl leading-relaxed"
          >
            Quotations, invoices, quality control, production scheduling and R&D, unified in one workspace, with AI built in for when you need it.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-8 sm:mt-12 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3"
          >
            <Link to="/request-demo">
              <Button size="lg" className="w-full sm:w-auto h-12 px-6 text-base">
                Request a demo <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto h-12 px-6 text-base">
                Sign in to your workspace
              </Button>
            </Link>
          </motion.div>
        </motion.div>

        {/* subtle grid backdrop */}
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 [background-image:linear-gradient(to_right,hsl(var(--border)/0.4)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--border)/0.4)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />
      </section>

      {/* WHAT IT IS */}
      <section className="border-t border-border/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32 grid sm:grid-cols-12 gap-8 sm:gap-10">
          <motion.div {...fadeUp} className="sm:col-span-4">
            <p className="text-sm tracking-widest uppercase text-muted-foreground">What it is</p>
          </motion.div>
          <motion.div {...fadeUp} className="sm:col-span-8 space-y-6 sm:space-y-8">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight leading-tight">
            Built for the way Indian polymer MSMEs actually run, not generic ERP bloat.
            </h2>
            <p className="text-base sm:text-lg text-muted-foreground leading-relaxed">
              Udyami consolidates the documents, schedules and inspections you already maintain across spreadsheets, paper and WhatsApp into a single, calm workspace. No retraining your team. No 6-month implementation.
            </p>
          </motion.div>
        </div>
      </section>

      {/* MODULES */}
      <section id="modules" className="border-t border-border/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
          <motion.div {...fadeUp} className="mb-10 sm:mb-16 max-w-2xl">
            <p className="text-sm tracking-widest uppercase text-muted-foreground mb-4">Modules</p>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight leading-tight">
              Five core modules. One workspace. One source of truth.
            </h2>
          </motion.div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-border/60 border border-border/60 rounded-2xl overflow-hidden">
            {modules.map((m, i) => (
              <motion.div
                key={m.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                className="bg-background p-6 sm:p-8 hover:bg-muted/30 transition-colors"
              >
                <m.icon className="h-5 w-5 mb-4 sm:mb-6" strokeWidth={1.5} />
                <h3 className="font-semibold mb-2">{m.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{m.desc}</p>
              </motion.div>
            ))}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: 0.25 }}
              className="bg-foreground text-background p-6 sm:p-8"
            >
              <Sparkles className="h-5 w-5 mb-4 sm:mb-6" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">Udyami AI</h3>
              <p className="text-sm opacity-80 leading-relaxed">An always-on consultant grounded in your live data. Optional, you stay in control.</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="border-t border-border/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
          <motion.div {...fadeUp} className="mb-10 sm:mb-16 max-w-2xl">
            <p className="text-sm tracking-widest uppercase text-muted-foreground mb-4">How it works</p>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight leading-tight">
              From signed contract to live workspace in under a week.
            </h2>
          </motion.div>
          <div className="space-y-px">
            {steps.map((s, i) => (
              <motion.div
                key={s.n}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                className="grid grid-cols-1 sm:grid-cols-12 gap-3 sm:gap-6 py-6 sm:py-8 border-t border-border/60 first:border-t-0"
              >
                <div className="sm:col-span-2 text-sm font-mono text-muted-foreground">{s.n}</div>
                <div className="sm:col-span-4">
                  <h3 className="text-base sm:text-lg font-semibold">{s.title}</h3>
                </div>
                <div className="sm:col-span-6">
                  <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">{s.body}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* TRUST */}
      <section id="trust" className="border-t border-border/40 bg-muted/20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32 grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-10">
          {[
            { icon: Lock, title: "Per-organization isolation", body: "Row-level security ensures one client never sees another client's data. Enforced at the database, not the app." },
            { icon: Database, title: "Your data, your control", body: "Export everything to CSV at any time. We never train models on your data." },
            { icon: Sparkles, title: "AI that stays in scope", body: "Udyami AI is locked to polymer manufacturing context. Hard guardrails against off-topic and prompt injection." },
          ].map((t, i) => (
            <motion.div
              key={t.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.07 }}
            >
              <t.icon className="h-5 w-5 mb-4 sm:mb-6" strokeWidth={1.5} />
              <h3 className="font-semibold mb-2">{t.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-32 lg:py-40 text-center">
          <motion.h2 {...fadeUp} className="text-3xl sm:text-4xl lg:text-6xl font-semibold tracking-tight leading-[1.05] max-w-3xl mx-auto">
            See Udyami running on your own production data.
          </motion.h2>
          <motion.p {...fadeUp} className="mt-6 sm:mt-8 text-base sm:text-lg text-muted-foreground max-w-xl mx-auto">
            A 30-minute personalized demo. No slides. We map your current workflow live.
          </motion.p>
          <motion.div {...fadeUp} className="mt-8 sm:mt-12 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center justify-center gap-3">
            <Link to="/request-demo">
              <Button size="lg" className="w-full sm:w-auto h-12 px-8 text-base">
                Request a demo <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm text-muted-foreground">
          <div>© {new Date().getFullYear()} Udyami. All rights reserved.</div>
          <div className="flex items-center gap-6">
            <Link to="/login" className="hover:text-foreground transition-colors">Login</Link>
            <Link to="/request-demo" className="hover:text-foreground transition-colors">Request demo</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
