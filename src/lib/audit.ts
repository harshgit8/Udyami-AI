import { supabase } from "@/integrations/supabase/client";

export async function logAudit(action: string, entity?: string, entityId?: string, payload?: Record<string, unknown>) {
  try {
    await supabase.from("audit_logs").insert([{
      action,
      entity: entity ?? null,
      entity_id: entityId ?? null,
      payload: (payload ?? {}) as Record<string, unknown>,
    }]);
  } catch (e) {
    console.error("Audit log failed:", e);
  }
}
