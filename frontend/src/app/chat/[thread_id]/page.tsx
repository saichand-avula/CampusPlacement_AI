"use client";

import { use, useEffect, useRef } from "react";
import { useChatContext } from "../components/ChatProvider";
import { useChat } from "../hooks/useChat";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

interface Props {
  params: Promise<{ thread_id: string }>;
}

/**
 * /chat/[thread_id] — Existing thread page.
 *
 * On mount:
 *   1. Loads messages from DB via useChat hook.
 *   2. If pendingMessage exists (from /chat page), sends it immediately.
 */
export default function ThreadPage({ params }: Props) {
  const { thread_id } = use(params);
  const { pendingMessage, setPendingMessage, refreshThreads } =
    useChatContext();
  const { messages, isStreaming, isLoading, sendMessage, scrollRef } =
    useChat(thread_id);

  // Track whether we've already consumed the pending message
  const pendingConsumed = useRef(false);

  useEffect(() => {
    if (pendingMessage && !pendingConsumed.current && !isLoading) {
      pendingConsumed.current = true;
      const msg = pendingMessage;
      setPendingMessage(null);

      sendMessage(msg).then(() => {
        refreshThreads();
      });
    }
  }, [
    pendingMessage,
    isLoading,
    sendMessage,
    setPendingMessage,
    refreshThreads,
  ]);

  const handleSend = async (content: string) => {
    await sendMessage(content);
    refreshThreads();
  };

  return (
    <>
      <ChatWindow
        messages={messages}
        isStreaming={isStreaming}
        isLoading={isLoading}
        scrollRef={scrollRef}
      />
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </>
  );
}
