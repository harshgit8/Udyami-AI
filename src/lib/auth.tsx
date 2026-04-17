import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "@/integrations/supabase/client";

export type AppRole = "super_admin" | "org_admin" | "org_user";

export interface UserProfile {
  id: string;
  org_id: string | null;
  full_name: string | null;
  email: string | null;
  phone: string | null;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  status: string;
  plan: string;
  max_users: number;
}

interface AuthContextValue {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  organization: Organization | null;
  roles: AppRole[];
  isSuperAdmin: boolean;
  isOrgAdmin: boolean;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [roles, setRoles] = useState<AppRole[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAuxData = useCallback(async (uid: string) => {
    const [profileRes, rolesRes] = await Promise.all([
      supabase.from("profiles").select("id,org_id,full_name,email,phone").eq("id", uid).maybeSingle(),
      supabase.from("user_roles").select("role").eq("user_id", uid),
    ]);

    const p = (profileRes.data as UserProfile | null) ?? null;
    setProfile(p);
    setRoles(((rolesRes.data ?? []) as { role: AppRole }[]).map((r) => r.role));

    if (p?.org_id) {
      const { data: org } = await supabase
        .from("organizations")
        .select("id,name,slug,status,plan,max_users")
        .eq("id", p.org_id)
        .maybeSingle();
      setOrganization((org as Organization | null) ?? null);
    } else {
      setOrganization(null);
    }
  }, []);

  useEffect(() => {
    // Set up listener FIRST
    const { data: sub } = supabase.auth.onAuthStateChange((_event, sess) => {
      setSession(sess);
      setUser(sess?.user ?? null);
      if (sess?.user) {
        // defer to avoid deadlock
        setTimeout(() => { void loadAuxData(sess.user.id); }, 0);
      } else {
        setProfile(null);
        setOrganization(null);
        setRoles([]);
      }
    });

    // Then check existing session
    void supabase.auth.getSession().then(async ({ data: { session: sess } }) => {
      setSession(sess);
      setUser(sess?.user ?? null);
      if (sess?.user) await loadAuxData(sess.user.id);
      setLoading(false);
    });

    return () => { sub.subscription.unsubscribe(); };
  }, [loadAuxData]);

  const signIn = useCallback(async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  }, []);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const refresh = useCallback(async () => {
    if (user) await loadAuxData(user.id);
  }, [user, loadAuxData]);

  const value: AuthContextValue = {
    user, session, profile, organization, roles,
    isSuperAdmin: roles.includes("super_admin"),
    isOrgAdmin: roles.includes("org_admin") || roles.includes("super_admin"),
    loading,
    signIn, signOut, refresh,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
