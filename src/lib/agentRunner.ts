const CHAT_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/ai-chat`;

export type CoreAgentId = "production" | "invoice" | "quality" | "rnd";

export interface AgentRunOptions {
  agent: CoreAgentId;
  prompt: string;
}

export interface AgentRunResult {
  content: string;
}

export async function runCoreAgent({ agent, prompt }: AgentRunOptions): Promise<AgentRunResult> {
  const payload = {
    messages: [
      {
        role: "user" as const,
        content: `[UDYAMI_AGENT:${agent.toUpperCase()}]\n${prompt}`,
      },
    ],
  };

  console.log("[AgentRunner] Dispatching agent run", {
    agent,
    url: CHAT_URL,
    payload,
  });

  const resp = await fetch(CHAT_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
    },
    body: JSON.stringify(payload),
  });

  console.log("[AgentRunner] HTTP response", {
    agent,
    status: resp.status,
    ok: resp.ok,
  });

  if (resp.status === 429) {
    throw new Error("Rate limit exceeded. Please try again in a moment.");
  }
  if (resp.status === 402) {
    throw new Error("Usage limit reached. Please add credits to continue.");
  }
  if (!resp.ok) {
    let errorBody: unknown = null;
    try {
      errorBody = await resp.json();
    } catch {
      // ignore
    }
    console.error("[AgentRunner] Error body", errorBody);
    const message =
      (errorBody as { error?: string } | null)?.error ?? `Agent call failed with status ${resp.status}`;
    throw new Error(message);
  }
  if (!resp.body) {
    throw new Error("No response body from agent");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let assistantContent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newlineIndex: number;
    while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
      let line = buffer.slice(0, newlineIndex);
      buffer = buffer.slice(newlineIndex + 1);

      if (line.endsWith("\r")) line = line.slice(0, -1);
      if (line.startsWith(":") || line.trim() === "") continue;
      if (!line.startsWith("data: ")) continue;

      const jsonStr = line.slice(6).trim();
      if (jsonStr === "[DONE]") break;

      try {
        const parsed = JSON.parse(jsonStr);
        const content = parsed.choices?.[0]?.delta?.content as string | undefined;
        if (content) {
          assistantContent += content;
        }
      } catch (err) {
        console.warn("[AgentRunner] Failed to parse SSE line", { line, err });
        buffer = line + "\n" + buffer;
        break;
      }
    }
  }

  console.log("[AgentRunner] Completed agent run", {
    agent,
    contentPreview: assistantContent.slice(0, 400),
  });

  return { content: assistantContent };
}

