"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useChatContext } from "./ChatProvider";

export default function ChatSidebar() {
  const { threads, sidebarOpen, setSidebarOpen } = useChatContext();
  const params = useParams<{ thread_id?: string }>();
  const activeThreadId = params?.thread_id;

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-14 left-0 z-40 h-[calc(100vh-3.5rem)] w-64
          transform border-r border-zinc-800/60 bg-zinc-925
          transition-transform duration-200 ease-in-out
          lg:translate-x-0
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="flex h-full flex-col">
          {/* New Chat Button */}
          <div className="p-3">
            <Link
              href="/chat"
              onClick={() => setSidebarOpen(false)}
              className="flex w-full items-center gap-2.5 rounded-lg border border-zinc-700/50 px-3.5 py-2.5 text-sm font-medium text-zinc-200 transition-all hover:border-zinc-600 hover:bg-zinc-800/50 active:scale-[0.98]"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              New Chat
            </Link>
          </div>

          {/* Thread List */}
          <nav className="flex-1 overflow-y-auto px-2 pb-4">
            {threads.length === 0 && (
              <p className="px-3 pt-4 text-xs text-zinc-500">
                No conversations yet
              </p>
            )}

            {threads.map((thread) => {
              const isActive = thread.thread_id === activeThreadId;

              return (
                <Link
                  key={thread.thread_id}
                  href={`/chat/${thread.thread_id}`}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    group flex items-center gap-2.5 rounded-lg px-3 py-2.5 mb-0.5
                    text-sm transition-colors
                    ${
                      isActive
                        ? "bg-zinc-800 text-zinc-100"
                        : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200"
                    }
                  `}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="shrink-0 opacity-50"
                  >
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <span className="truncate">{thread.title}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
