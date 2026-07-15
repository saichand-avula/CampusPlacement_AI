"use client";

import type { RefObject } from "react";
import type { Message } from "../lib/types";
import ChatMessage from "./ChatMessage";
import LoadingMessage from "./LoadingMessage";

interface Props {
  messages: Message[];
  isStreaming: boolean;
  isLoading: boolean;
  scrollRef: RefObject<HTMLDivElement | null>;
}

export default function ChatWindow({
  messages,
  isStreaming,
  isLoading,
  scrollRef,
}: Props) {
  // Show loading indicator when streaming has started
  // but assistant hasn't sent any tokens yet
  const lastMsg = messages[messages.length - 1];
  const showLoadingDots =
    isStreaming && lastMsg?.role === "assistant" && lastMsg.content === "";

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 lg:px-16"
    >
      {/* Empty state */}
      {!isLoading && messages.length === 0 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-600/20 ring-1 ring-indigo-500/10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-indigo-400"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h2 className="mb-2 text-lg font-semibold text-zinc-200">
            Start a conversation
          </h2>
          <p className="max-w-sm text-sm text-zinc-500">
            Type a message below to begin chatting with your AI assistant.
          </p>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="flex h-full items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500" />
        </div>
      )}

      {/* Messages */}
      {!isLoading && (
        <div className="mx-auto max-w-3xl">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {showLoadingDots && <LoadingMessage />}
        </div>
      )}
    </div>
  );
}
