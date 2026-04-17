import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";

export default function Login() {
  const { signIn, user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const from = (location.state as { from?: string } | null)?.from ?? "/app";

  useEffect(() => { document.title = "Sign in — Udyami"; }, []);

  useEffect(() => {
    if (!loading && user) navigate(from, { replace: true });
  }, [user, loading, from, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const { error } = await signIn(email.trim(), password);
    setSubmitting(false);
    if (error) {
      toast({ title: "Sign in failed", description: error, variant: "destructive" });
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-foreground text-background">
        <Link to="/" className="font-semibold tracking-tight text-lg">Udyami</Link>
        <div>
          <p className="text-sm tracking-widest uppercase opacity-60 mb-6">Workspace</p>
          <p className="text-3xl font-semibold tracking-tight leading-tight max-w-md">
            One calm workspace for your entire manufacturing operation.
          </p>
        </div>
        <p className="text-xs opacity-60">© {new Date().getFullYear()} Udyami</p>
      </div>

      <div className="flex flex-col">
        <div className="p-6">
          <Link to="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" /> Back to home
          </Link>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-sm"
          >
            <h1 className="text-3xl font-semibold tracking-tight">Sign in</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Use the credentials issued by your organization administrator.
            </p>

            <form onSubmit={onSubmit} className="mt-10 space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email">Work email</Label>
                <Input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <Button type="submit" disabled={submitting} className="w-full h-11">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign in"}
              </Button>
            </form>

            <p className="mt-8 text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link to="/request-demo" className="text-foreground underline underline-offset-4 hover:no-underline">
                Request a demo
              </Link>
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
