import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
//import Artifact from "./Artifact";

import { useContext, createContext } from "react";

interface SidebarContextType {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}
const SidebarContext = createContext<SidebarContextType>({
  isSidebarOpen: false,
  toggleSidebar: () => {},
});

const MainContent = () => {
  return (
    <div className="flex flex-row h-full w-full">
      <Sidebar />
      <ChatWindow />
      <div className="hidden md:block">
       {/* <Artifact /> */}
      </div>
    </div>
  );
};

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
};

export default MainContent;
