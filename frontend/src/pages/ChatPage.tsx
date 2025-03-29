import MainContent from "../components/chat/MainContent";
import Navbar from "../components/Navbar";

const ChatPage = () => {
  return (
    <div className="flex flex-col h-screen w-screen">
      <Navbar />
      <MainContent />
    </div>
  );
};

export default ChatPage;
