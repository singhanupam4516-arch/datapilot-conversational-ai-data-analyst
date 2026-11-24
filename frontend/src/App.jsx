import { useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { UploadPage } from "./pages/UploadPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ChatPage } from "./pages/ChatPage";

function App() {
  const [session, setSession] = useState(null);
  const [view, setView] = useState("upload");

  const handleUploadComplete = (uploaded) => {
    setSession(uploaded);
    setView("dashboard");
  };

  const handleReset = () => {
    setSession(null);
    setView("upload");
  };

  const handleNavigate = (nextView) => {
    if (nextView !== "upload" && !session) return;
    setView(nextView);
  };

  return (
    <div className="app-shell">
      <Sidebar session={session} activeView={view} onNavigate={handleNavigate} onReset={handleReset} />
      <main className="main-content">
        {view === "upload" && <UploadPage onUploadComplete={handleUploadComplete} />}
        {view === "dashboard" && session && (
          <DashboardPage session={session} onGoToChat={() => setView("chat")} />
        )}
        {view === "chat" && session && <ChatPage session={session} />}
      </main>
    </div>
  );
}

export default App;
