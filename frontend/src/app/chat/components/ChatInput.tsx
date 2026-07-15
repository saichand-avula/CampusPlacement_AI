"use client";

import { useState, useRef, useCallback, type KeyboardEvent } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setValue("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-grow textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  return (
    <div className="border-t border-zinc-800/60 bg-zinc-950/90 backdrop-blur-md px-4 py-3 sm:px-8 lg:px-16">
      <div className="mx-auto flex max-w-3xl items-end gap-3">
        {/* Textarea */}
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={
              disabled ? "Waiting for response…" : "Type a message…"
            }
            rows={1}
            className="
              w-full resize-none rounded-xl border border-zinc-700/50
              bg-zinc-800/50 px-4 py-3 pr-12 text-sm text-zinc-100
              placeholder-zinc-500 outline-none
              transition-colors
              focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20
              disabled:cursor-not-allowed disabled:opacity-50
            "
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="
            flex h-11 w-11 shrink-0 items-center justify-center
            rounded-xl bg-indigo-600 text-white
            transition-all
            hover:bg-indigo-500 active:scale-95
            disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-indigo-600
          "
          aria-label="Send message"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>

      <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-zinc-600">
        Press Enter to send · Shift + Enter for new line
      </p>
    </div>
  );
}
