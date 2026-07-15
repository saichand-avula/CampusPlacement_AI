"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Message } from "../lib/types";
import { fetchMessages, streamMessage } from "../lib/api";

interface UseChatReturn {
  messages: Message[];
  isStreaming: boolean;
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  scrollRef: React.RefObject<HTMLDivElement | null>;
}

/**
 * Custom hook encapsulating all chat state & logic for a thread.
 *
 * @param threadId - When provided, loads existing messages on mount.
 */
export function useChat(threadId?: string): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // ── Load existing messages ───────────────
  useEffect(() => {
    if (!threadId) {
      setMessages([]);
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    (async () => {
      setIsLoading(true);
      try {
        const data = await fetchMessages(threadId);
        if (!cancelled) setMessages(data);
      } catch (err) {
        console.error("Failed to load messages:", err);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [threadId]);

  // ── Auto-scroll ──────────────────────────
  useEffect(() => {
    const el = scrollRef.current;
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  // ── Send message & stream response ───────
  const sendMessage = useCallback(
    async (content: string) => {
      if (!threadId || isStreaming) return;

      // Optimistically add user message
      const userMsg: Message = {
        id: `temp-user-${Date.now()}`,
        thread_id: threadId,
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };

      // Add user message + empty assistant placeholder
      const assistantMsg: Message = {
        id: `temp-assistant-${Date.now()}`,
        thread_id: threadId,
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);

      await streamMessage(
        threadId,
        content,
        // onToken
        (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...last,
              content: last.content + token,
            };
            return updated;
          });
        },
        // onDone
        () => {
          setIsStreaming(false);
        },
        // onError
        (error) => {
          console.error("Stream error:", error);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...last,
              content: last.content || "Sorry, something went wrong.",
            };
            return updated;
          });
          setIsStreaming(false);
        }
      );
    },
    [threadId, isStreaming]
  );

  return { messages, isStreaming, isLoading, sendMessage, scrollRef };
}
