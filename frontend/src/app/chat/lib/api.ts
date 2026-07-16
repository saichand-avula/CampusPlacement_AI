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

/**
 * Upload a JD PDF for a thread. Returns the saved path.
 */
export async function uploadJD(
  threadId: string,
  file: File
): Promise<{ jd_path: string; filename: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload/jd/${threadId}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to upload JD");
  }

  return res.json();
}

/**
 * Fetch assistant state for a thread (workflow_initialized, jd_path, etc.)
 */
export async function getAssistantState(threadId: string): Promise<AssistantStateResponse> {
  const res = await fetch(`${API_BASE}/chat/assistant-state/${threadId}`);

  if (!res.ok) {
    throw new Error("Failed to fetch assistant state");
  }

  return res.json();
}

/**
 * Fetch the finalized workflow (mystate) after workflow is initialized.
 */
export async function getWorkflowState(threadId: string): Promise<WorkflowStateResponse | null> {
  const res = await fetch(`${API_BASE}/chat/workflow-state/${threadId}`);

  if (res.status === 404) return null;

  if (!res.ok) {
    throw new Error("Failed to fetch workflow state");
  }

  return res.json();
}

/**
 * Fetch all templates for a user.
 */
export async function fetchTemplates(
  userId: string
): Promise<{ templates: { name: string; fields: unknown[] }[]; count: number }> {
  const res = await fetch(`${API_BASE}/chat/templates/${userId}`);

  if (!res.ok) {
    throw new Error("Failed to fetch templates");
  }

  return res.json();
}

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

export interface AssistantStateResponse {
  workflow_initialized: boolean;
  initial_jd_path: string | null;
  initial_company_name: string | null;
  initial_form_template_name: string | null;
  initial_deadline: string | null;
  initial_job_title: string[] | null;
  initial_employment_type: string | null;
  initial_work_location: string | null;
  initial_stipend: string | null;
  initial_ctc: string | null;
  initial_eligibility: string | null;
  initial_branches: string | null;
}

export interface EOIFields {
  company_name: string;
  company_website?: string;
  linkedin_link?: string;
  job_title: string[];
  employment_type?: string;
  work_location?: string;
  stipend?: string;
  ctc?: string;
  duration?: string;
  eligibility?: string;
  branches?: string;
  job_description?: string;
  selection_process?: string[];
  other_benefits?: string;
  assignment_required: boolean;
  assignment_link?: string;
}

export interface WorkflowStateResponse {
  thread_id: string;
  user_id: string;
  jd_path: string;
  jd_text: string;
  deadline: string;
  form_template_name: string;
  eoi_fields: EOIFields | null;
  form_fields: Array<{
    label: string;
    field_type: string;
    required: boolean;
    options: string[];
  }> | null;
  form_link: string | null;
  form_sheet_link: string | null;
  form_drive_link: string | null;
  raw_links: string[];
}
