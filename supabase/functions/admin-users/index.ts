// Admin-only edge function to provision orgs and users.
// Verifies the caller is super_admin via JWT before performing any action.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

interface CreateUserBody {
  action: "create_user";
  email: string;
  password: string;
  full_name: string;
  org_id: string;
  role: "super_admin" | "org_admin" | "org_user";
}

interface DeleteUserBody {
  action: "delete_user";
  user_id: string;
}

interface BootstrapBody {
  action: "bootstrap_super_admin";
  email: string;
  password: string;
  full_name: string;
}

type Body = CreateUserBody | DeleteUserBody | BootstrapBody;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
    const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const ANON = Deno.env.get("SUPABASE_ANON_KEY")!;

    const admin = createClient(SUPABASE_URL, SERVICE_ROLE, {
      auth: { autoRefreshToken: false, persistSession: false },
    });

    const body = (await req.json()) as Body;

    // ---------- BOOTSTRAP: only allowed if NO super_admin exists yet ----------
    if (body.action === "bootstrap_super_admin") {
      const { count, error: countErr } = await admin
        .from("user_roles")
        .select("*", { count: "exact", head: true })
        .eq("role", "super_admin");

      if (countErr) throw countErr;
      if ((count ?? 0) > 0) {
        return new Response(
          JSON.stringify({ error: "Super admin already exists" }),
          { status: 403, headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );
      }

      // Ensure Udyami HQ org exists
      let hqId: string;
      const { data: existing } = await admin
        .from("organizations")
        .select("id")
        .eq("slug", "udyami-hq")
        .maybeSingle();

      if (existing) {
        hqId = existing.id;
      } else {
        const { data: newOrg, error: orgErr } = await admin
          .from("organizations")
          .insert({
            name: "Udyami HQ",
            slug: "udyami-hq",
            status: "active",
            plan: "internal",
            max_users: 999,
            notes: "Internal Udyami operations org",
          })
          .select("id")
          .single();
        if (orgErr) throw orgErr;
        hqId = newOrg.id;
      }

      const { data: created, error: cErr } = await admin.auth.admin.createUser({
        email: body.email,
        password: body.password,
        email_confirm: true,
        user_metadata: {
          full_name: body.full_name,
          org_id: hqId,
          role: "super_admin",
        },
      });
      if (cErr) throw cErr;

      return new Response(
        JSON.stringify({ ok: true, user_id: created.user?.id, org_id: hqId }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // ---------- All other actions require super_admin JWT ----------
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(JSON.stringify({ error: "Missing Authorization" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const userClient = createClient(SUPABASE_URL, ANON, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: userRes, error: userErr } = await userClient.auth.getUser();
    if (userErr || !userRes.user) {
      return new Response(JSON.stringify({ error: "Invalid token" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const { data: roles, error: rolesErr } = await admin
      .from("user_roles")
      .select("role")
      .eq("user_id", userRes.user.id);
    if (rolesErr) throw rolesErr;
    const isSuper = roles?.some((r) => r.role === "super_admin");
    if (!isSuper) {
      return new Response(JSON.stringify({ error: "Forbidden" }), {
        status: 403,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (body.action === "create_user") {
      // Enforce per-org user cap
      const { data: org, error: oErr } = await admin
        .from("organizations")
        .select("max_users")
        .eq("id", body.org_id)
        .single();
      if (oErr) throw oErr;

      const { count, error: cntErr } = await admin
        .from("profiles")
        .select("*", { count: "exact", head: true })
        .eq("org_id", body.org_id);
      if (cntErr) throw cntErr;

      if ((count ?? 0) >= (org.max_users ?? 4)) {
        return new Response(
          JSON.stringify({ error: `Org has reached its limit of ${org.max_users} users` }),
          { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );
      }

      const { data, error } = await admin.auth.admin.createUser({
        email: body.email,
        password: body.password,
        email_confirm: true,
        user_metadata: {
          full_name: body.full_name,
          org_id: body.org_id,
          role: body.role,
        },
      });
      if (error) throw error;
      return new Response(JSON.stringify({ ok: true, user_id: data.user?.id }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (body.action === "delete_user") {
      const { error } = await admin.auth.admin.deleteUser(body.user_id);
      if (error) throw error;
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Unknown action" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    console.error("admin-users error:", msg);
    return new Response(JSON.stringify({ error: msg }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
