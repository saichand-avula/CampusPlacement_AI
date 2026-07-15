"use client";

import { useChatContext } from "./ChatProvider";

export default function Navbar() {
  const { setSidebarOpen, sidebarOpen } = useChatContext();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-md px-4">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="mr-3 rounded-md p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors lg:hidden"
        aria-label="Toggle sidebar"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Logo / Title */}
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-sm font-bold shadow-md shadow-indigo-500/20">
          C
        </div>
        <h1 className="text-base font-semibold tracking-tight text-zinc-100">
          Campus Placement AI
        </h1>
      </div>
    </header>
  );
}
