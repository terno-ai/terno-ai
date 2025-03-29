import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
import Sandbox from "./Sandbox";

const MainContent = () => {
  return (
    <div className="flex flex-row h-full w-full">
      <Sidebar />
      <ChatWindow />
      <Sandbox />
    </div>
  );
};

export default MainContent;
