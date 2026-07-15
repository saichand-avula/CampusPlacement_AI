export default function LoadingMessage() {
  return (
    <div className="flex w-full justify-start mb-5">
      {/* Avatar */}
      <div className="mr-3 mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-xs font-bold text-white shadow-sm">
        AI
      </div>

      {/* Pulsing dots */}
      <div className="rounded-2xl rounded-bl-md bg-zinc-800/70 px-5 py-4">
        <div className="flex items-center gap-1.5">
          <span className="loading-dot h-2 w-2 rounded-full bg-zinc-400" />
          <span className="loading-dot h-2 w-2 rounded-full bg-zinc-400" />
          <span className="loading-dot h-2 w-2 rounded-full bg-zinc-400" />
        </div>
      </div>
    </div>
  );
}
