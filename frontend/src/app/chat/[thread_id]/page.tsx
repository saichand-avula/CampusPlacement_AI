"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import { useChatContext } from "../components/ChatProvider";
import { useChat } from "../hooks/useChat";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import JDUploadPopup from "../components/JDUploadPopup";
import WorkflowStatePanel from "../components/WorkflowStatePanel";
import {
  getAssistantState,
  getWorkflowState,
  type AssistantStateResponse,
  type WorkflowStateResponse,
} from "../lib/api";

interface Props {
  params: Promise<{ thread_id: string }>;
}

export default function ThreadPage({ params }: Props) {
  const { thread_id } = use(params);
  const { pendingMessage, setPendingMessage, refreshThreads } =
    useChatContext();
  const { messages, isStreaming, isLoading, sendMessage, scrollRef } =
    useChat(thread_id);

  // ── Assistant & workflow state ───────────────
  const [assistantState, setAssistantState] =
    useState<AssistantStateResponse | null>(null);
  const [workflowState, setWorkflowState] =
    useState<WorkflowStateResponse | null>(null);
  const [localJdPath, setLocalJdPath] = useState<string | null>(null);
  const [showWorkflowMobile, setShowWorkflowMobile] = useState(false);
  const [workflowLoading, setWorkflowLoading] = useState(false);

  // Track whether we've already consumed the pending message
  const pendingConsumed = useRef(false);
  // Retry timer ref for workflow state polling
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Fetch workflow state with retries ─────────
  const fetchWorkflowState = useCallback(
    async (retries = 8, delayMs = 1200) => {
      for (let i = 0; i < retries; i++) {
        // Small initial wait to let the store write propagate
        await new Promise((res) => {
          retryRef.current = setTimeout(res, i === 0 ? 500 : delayMs);
        });
        try {
          setWorkflowLoading(true);
          const wState = await getWorkflowState(thread_id);
          if (wState) {
            setWorkflowState(wState);
            setWorkflowLoading(false);
            return;
          }
        } catch {
          // 404 = not ready yet, keep retrying
        }
      }
      setWorkflowLoading(false);
    },
    [thread_id]
  );

  // ── Fetch assistant state ─────────────────────
  const fetchState = useCallback(
    async (triggerWorkflowFetch = false) => {
      try {
        const aState = await getAssistantState(thread_id);
        setAssistantState(aState);

        // Sync local JD path from state if not already set locally
        if (aState.initial_jd_path && !localJdPath) {
          setLocalJdPath(aState.initial_jd_path);
        }

        // Always try fetching workflow results on mount or after a message.
        // The workflow_initialized flag can be lost after a server restart,
        // but store results survive — so check the store directly too.
        if (triggerWorkflowFetch || !workflowState) {
          fetchWorkflowState();
        }
      } catch {
        // Silently ignore — thread may not have state yet
      }
    },
    [thread_id, localJdPath, workflowState, fetchWorkflowState]
  );

  // Fetch state on mount
  useEffect(() => {
    fetchState();
  }, [thread_id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Cleanup retry timer on unmount
  useEffect(() => {
    return () => {
      if (retryRef.current) clearTimeout(retryRef.current);
    };
  }, []);

  // ── Pending message (from new chat page) ─────
  useEffect(() => {
    if (pendingMessage && !pendingConsumed.current && !isLoading) {
      pendingConsumed.current = true;
      const msg = pendingMessage;
      setPendingMessage(null);

      sendMessage(msg).then(() => {
        refreshThreads();
        fetchState(true);
      });
    }
  }, [
    pendingMessage,
    isLoading,
    sendMessage,
    setPendingMessage,
    refreshThreads,
    fetchState,
  ]);

  const handleSend = async (content: string) => {
    await sendMessage(content);
    refreshThreads();
    // Re-fetch state after each message — pass true to also re-fetch workflow state
    await fetchState(true);
  };

  const handleJDUploaded = (jdPath: string, filename: string) => {
    setLocalJdPath(jdPath);
    setAssistantState((prev) =>
      prev ? { ...prev, initial_jd_path: jdPath } : null
    );
    console.log(`JD uploaded: ${filename} → ${jdPath}`);
  };

  // Treat as initialized if the flag is set OR if we already have workflow results
  // (results survive server restarts even when the checkpointer flag is lost)
  const workflowInitialized = (assistantState?.workflow_initialized ?? false) || !!workflowState;
  const effectiveJdPath = localJdPath || assistantState?.initial_jd_path || null;

  return (
    <div className="flex flex-col h-full">
      {/* ─── JD Upload sticky banner (hidden after workflow starts) ─── */}
      {!workflowInitialized && (
        <JDUploadPopup
          threadId={thread_id}
          currentJdPath={effectiveJdPath}
          onUploaded={handleJDUploaded}
        />
      )}

      {/* ─── Mobile workflow toggle button ─── */}
      {workflowInitialized && (
        <div className="flex lg:hidden items-center justify-between px-4 py-2 border-b border-zinc-800/60 bg-zinc-900/80">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-medium text-zinc-300">Workflow Active</span>
          </div>
          <button
            id="workflow-mobile-toggle"
            onClick={() => setShowWorkflowMobile((v) => !v)}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
          >
            {showWorkflowMobile ? "Hide Results" : "Show Results →"}
          </button>
        </div>
      )}

      {/* ─── Mobile workflow panel (full width, collapsible) ─── */}
      {workflowInitialized && showWorkflowMobile && (
        <div className="lg:hidden border-b border-zinc-800/60 bg-zinc-950/80 p-3 max-h-96 overflow-y-auto">
          {workflowLoading && !workflowState ? (
            <div className="flex items-center justify-center py-8 gap-2">
              <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-zinc-400">Loading workflow results…</span>
            </div>
          ) : workflowState ? (
            <WorkflowStatePanel state={workflowState} />
          ) : (
            <p className="text-xs text-zinc-500 text-center py-4">
              Workflow is running — results will appear here shortly.
            </p>
          )}
        </div>
      )}

      {/* ─── Main content: chat + optional workflow panel ─── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat column */}
        <div className="flex flex-col flex-1 min-w-0">
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            isLoading={isLoading}
            scrollRef={scrollRef}
          />
          <ChatInput onSend={handleSend} disabled={isStreaming} />
        </div>

        {/* Workflow panel — right sidebar on lg+ */}
        {workflowInitialized && (
          <div
            className="hidden lg:flex flex-col w-80 xl:w-96 border-l border-zinc-800/60
              bg-zinc-950/50 overflow-y-auto p-3 gap-3 flex-shrink-0"
          >
            {workflowLoading && !workflowState ? (
              <div className="flex flex-col items-center justify-center h-40 gap-3">
                <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-xs text-zinc-400">Loading workflow results…</p>
              </div>
            ) : workflowState ? (
              <WorkflowStatePanel state={workflowState} />
            ) : (
              <div className="flex flex-col items-center justify-center h-40 gap-2 text-center px-4">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                    className="w-4 h-4 text-indigo-400">
                    <path d="M9 11l3 3L22 4" />
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                  </svg>
                </div>
                <p className="text-xs text-zinc-400">
                  Workflow started — results will appear here once processing completes.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
