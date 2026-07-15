import { ChatProvider } from "./components/ChatProvider";
import Navbar from "./components/Navbar";
import ChatSidebar from "./components/ChatSidebar";

export const metadata = {
  title: "Chat — Campus Placement AI",
};

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatProvider>
      <Navbar />

      <div className="flex pt-14 h-screen">
        <ChatSidebar />

        {/* Main content area — pushed right by sidebar on desktop */}
        <main className="flex flex-1 flex-col lg:ml-64">{children}</main>
      </div>
    </ChatProvider>
  );
}
