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
  // Start as true when threadId is present so the pending-message effect
  // waits until the initial fetchMessages finishes before sending.
  const [isLoading, setIsLoading] = useState(!!threadId);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  // Ref so the fetchMessages effect can check streaming state without
  // needing isStreaming in its dependency array (avoids re-runs mid-stream).
  const isStreamingRef = useRef(false);

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
        if (!cancelled) {
          // Don't overwrite messages if we're currently streaming
          // (the pending-message send may have already started).
          if (!isStreamingRef.current) {
            setMessages(data);
          }
        }
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
      isStreamingRef.current = true;
      setIsStreaming(true);

      await streamMessage(
        threadId,
        content,
        // onToken
        (token) => {
          setMessages((prev) => {
            if (prev.length === 0) return prev;
            const updated = [...prev];
            const last = updated[updated.length - 1];
            // Guard: last must exist and have a string content property
            if (!last || typeof last.content !== "string") return prev;
            updated[updated.length - 1] = {
              ...last,
              content: last.content + token,
            };
            return updated;
          });
        },
        // onDone
        () => {
          isStreamingRef.current = false;
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
          isStreamingRef.current = false;
          setIsStreaming(false);
        }
      );
    },
    [threadId, isStreaming]
  );

  return { messages, isStreaming, isLoading, sendMessage, scrollRef };
}
