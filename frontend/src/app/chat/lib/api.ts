import { ChatThread, Message } from "./types";

const API_BASE = "http://localhost:8000";

/**
 * Create a new thread. Returns the thread_id.
 */
export async function createThread(): Promise<{ thread_id: string }> {
  const res = await fetch(`${API_BASE}/chat/new`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to create thread");
  }

  return res.json();
}

/**
 * Fetch all chat threads for the current user.
 */
export async function fetchThreads(): Promise<ChatThread[]> {
  const res = await fetch(`${API_BASE}/chat/list`);

  if (!res.ok) {
    throw new Error("Failed to fetch threads");
  }

  return res.json();
}

/**
 * Fetch all messages for a specific thread.
 */
export async function fetchMessages(threadId: string): Promise<Message[]> {
  const res = await fetch(`${API_BASE}/chat/${threadId}`);

  if (!res.ok) {
    throw new Error("Failed to fetch messages");
  }

  return res.json();
}

/**
 * Send a message and stream the assistant response via SSE.
 *
 * @param threadId  - The thread to send to
 * @param message   - The user message
 * @param onToken   - Callback fired for each streamed token
 * @param onDone    - Callback fired when streaming finishes
 * @param onError   - Callback fired on error
 */
export async function streamMessage(
  threadId: string,
  message: string,
  onToken: (token: string) => void,
  onDone: () => void,
  onError?: (error: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/${threadId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const text = await res.text();
    onError?.(text || "Failed to send message");
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    onError?.("No response stream");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Parse SSE frames: "data: ...\n\n"
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const frame of lines) {
        const line = frame.trim();

        if (!line.startsWith("data: ")) continue;

        const payload = line.slice(6); // strip "data: "

        if (payload === "[DONE]") {
          onDone();
          return;
        }

        try {
          const parsed = JSON.parse(payload);

          if (parsed.error) {
            onError?.(parsed.error);
            return;
          }

          if (parsed.token) {
            onToken(parsed.token);
          }
        } catch {
          // Malformed JSON — skip
        }
      }
    }

    // Stream ended without [DONE]
    onDone();
  } finally {
    reader.releaseLock();
  }
}
