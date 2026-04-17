// One-time setup page to create the very first super-admin account.
// The edge function refuses if a super_admin already exists, so this is safe to leave deployed.
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

export default function Bootstrap() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { document.title = "Initial setup — Udyami"; }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const { data, error } = await supabase.functions.invoke("admin-users", {
      body: {
        action: "bootstrap_super_admin",
        email: email.trim(),
        password,
        full_name: fullName.trim() || "Super Admin",
      },
    });
    setSubmitting(false);
    if (error || (data as { error?: string })?.error) {
      const msg = (data as { error?: string })?.error || error?.message || "Failed";
      toast({ title: "Bootstrap failed", description: msg, variant: "destructive" });
      return;
    }
    toast({ title: "Super-admin created", description: "You can now sign in." });
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen grid place-items-center p-6 bg-background">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="flex items-center gap-3 mb-8">
          <ShieldCheck className="h-6 w-6" strokeWidth={1.5} />
          <span className="text-sm tracking-widest uppercase text-muted-foreground">One-time setup</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Create the first super-admin</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          This runs once. After a super-admin exists, this page will refuse new requests.
        </p>

        <form onSubmit={onSubmit} className="mt-10 space-y-5">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full name</Label>
            <Input id="full_name" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Anup Patil" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <Button type="submit" disabled={submitting} className="w-full h-11">
            {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create super-admin"}
          </Button>
        </form>

        <p className="mt-8 text-sm text-muted-foreground">
          <Link to="/" className="hover:text-foreground transition-colors underline underline-offset-4">Back to home</Link>
        </p>
      </motion.div>
    </div>
  );
}
