"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";
import { ChatThread } from "../lib/types";
import { fetchThreads } from "../lib/api";

interface ChatContextValue {
  /** All chat threads for the sidebar */
  threads: ChatThread[];
  /** Re-fetch the thread list from the backend */
  refreshThreads: () => Promise<void>;
  /** Message queued by /chat page to be sent after navigation */
  pendingMessage: string | null;
  /** Set a pending message (consumed by [thread_id] page) */
  setPendingMessage: (msg: string | null) => void;
  /** Sidebar open state (for mobile toggle) */
  sidebarOpen: boolean;
  /** Toggle sidebar visibility */
  setSidebarOpen: (open: boolean) => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const refreshThreads = useCallback(async () => {
    try {
      const data = await fetchThreads();
      setThreads(data);
    } catch (err) {
      console.error("Failed to fetch threads:", err);
    }
  }, []);

  useEffect(() => {
    refreshThreads();
  }, [refreshThreads]);

  return (
    <ChatContext.Provider
      value={{
        threads,
        refreshThreads,
        pendingMessage,
        setPendingMessage,
        sidebarOpen,
        setSidebarOpen,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext(): ChatContextValue {
  const ctx = useContext(ChatContext);

  if (!ctx) {
    throw new Error("useChatContext must be used inside <ChatProvider>");
  }

  return ctx;
}
