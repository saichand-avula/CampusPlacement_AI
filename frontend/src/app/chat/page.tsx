"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useChatContext } from "./components/ChatProvider";
import { createThread } from "./lib/api";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

/**
 * /chat — New chat landing page.
 *
 * When the user sends their first message:
 *   1. Creates a new thread via POST /chat/new
 *   2. Stores the message in context (pendingMessage)
 *   3. Navigates to /chat/{thread_id}
 *   4. The thread page picks up the pending message and starts streaming
 */
export default function NewChatPage() {
  const router = useRouter();
  const { setPendingMessage, refreshThreads } = useChatContext();
  const [isCreating, setIsCreating] = useState(false);

  const handleSend = async (content: string) => {
    if (isCreating) return;

    setIsCreating(true);

    try {
      const { thread_id } = await createThread();

      // Store message for the thread page to pick up
      setPendingMessage(content);

      // Refresh sidebar to show new thread
      await refreshThreads();

      // Navigate to thread
      router.push(`/chat/${thread_id}`);
    } catch (err) {
      console.error("Failed to create thread:", err);
      setIsCreating(false);
    }
  };

  return (
    <>
      <ChatWindow
        messages={[]}
        isStreaming={false}
        isLoading={false}
        scrollRef={{ current: null }}
      />
      <ChatInput onSend={handleSend} disabled={isCreating} />
    </>
  );
}
