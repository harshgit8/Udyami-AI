import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, CheckCircle2, Loader2 } from "lucide-react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

const schema = z.object({
  business_name: z.string().trim().min(2, "Required").max(120),
  contact_name: z.string().trim().min(2, "Required").max(80),
  email: z.string().trim().email("Invalid email").max(160),
  phone: z.string().trim().max(20).optional().or(z.literal("")),
  company_size: z.string().min(1, "Select a size"),
  message: z.string().trim().max(800).optional().or(z.literal("")),
});

const sizes = ["1–10", "11–50", "51–200", "201–500", "500+"];

export default function RequestDemo() {
  const { toast } = useToast();
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [form, setForm] = useState({
    business_name: "", contact_name: "", email: "", phone: "",
    company_size: "", message: "",
  });

  useEffect(() => { document.title = "Request a demo — Udyami"; }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = schema.safeParse(form);
    if (!parsed.success) {
      const first = Object.values(parsed.error.flatten().fieldErrors)[0]?.[0];
      toast({ title: "Check your details", description: first ?? "Invalid input", variant: "destructive" });
      return;
    }
    setSubmitting(true);
    const { error } = await supabase.from("demo_requests").insert({
      business_name: parsed.data.business_name,
      contact_name: parsed.data.contact_name,
      email: parsed.data.email,
      phone: parsed.data.phone || null,
      company_size: parsed.data.company_size,
      message: parsed.data.message || null,
      source: "landing",
    });
    setSubmitting(false);
    if (error) {
      toast({ title: "Couldn't submit", description: error.message, variant: "destructive" });
      return;
    }
    setDone(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="font-semibold tracking-tight text-lg">Udyami</Link>
          <Link to="/login"><Button variant="ghost" size="sm">Login</Button></Link>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-6 py-16 sm:py-24">
        <Link to="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors mb-10">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to home
        </Link>

        {done ? (
          <motion.div
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <CheckCircle2 className="h-12 w-12 mx-auto mb-6" strokeWidth={1.5} />
            <h1 className="text-3xl font-semibold tracking-tight">Thank you.</h1>
            <p className="mt-4 text-muted-foreground max-w-md mx-auto">
              We've received your request. A member of our team will reach out within 1 business day to schedule your demo.
            </p>
            <Link to="/" className="inline-block mt-10">
              <Button variant="outline">Return home</Button>
            </Link>
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <p className="text-sm tracking-widest uppercase text-muted-foreground mb-4">Request a demo</p>
            <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight leading-[1.1]">
              Let's see Udyami on your data.
            </h1>
            <p className="mt-6 text-lg text-muted-foreground">
              Tell us a bit about your business. We'll set up a personalized 30-minute walkthrough.
            </p>

            <form onSubmit={onSubmit} className="mt-12 space-y-6">
              <div className="grid sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="business_name">Business name</Label>
                  <Input id="business_name" required value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="contact_name">Your name</Label>
                  <Input id="contact_name" required value={form.contact_name} onChange={(e) => setForm({ ...form, contact_name: e.target.value })} />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="email">Work email</Label>
                  <Input id="email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone (optional)</Label>
                  <Input id="phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Company size</Label>
                <Select value={form.company_size} onValueChange={(v) => setForm({ ...form, company_size: v })}>
                  <SelectTrigger><SelectValue placeholder="Select team size" /></SelectTrigger>
                  <SelectContent>
                    {sizes.map((s) => <SelectItem key={s} value={s}>{s} employees</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="message">What are you trying to solve? (optional)</Label>
                <Textarea id="message" rows={4} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
              </div>

              <Button type="submit" disabled={submitting} size="lg" className="w-full sm:w-auto h-11 px-8">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit request"}
              </Button>
            </form>
          </motion.div>
        )}
      </div>
    </div>
  );
}
