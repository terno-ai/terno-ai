import Split from "react-split";
import HomePageContent from "../components/HomePageContent";
import Sidebar from "../components/Sidebar";
import { DataSourceProvider } from "../components/ui/datasource-context";
import gutter from "../components/ui/gutter";
import Hotjar from "@hotjar/browser";
import { createContext, useContext, useState, useEffect } from "react";  

interface SidebarContextType {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}
const SidebarContext = createContext<SidebarContextType>({
  isSidebarOpen: false,
  toggleSidebar: () => {},
});



const Home = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const siteId = 5244049;
  const hotjarVersion = 6;

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  Hotjar.init(siteId, hotjarVersion);

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <SidebarContext.Provider value={{ isSidebarOpen, toggleSidebar }}> 
      <DataSourceProvider>
        
        <Split
          key={isMobile ? "mobile" : "desktop"}
          className="flex w-full h-full overflow-hidden"
          sizes={[20, 80]}
          minSize={100}
          expandToMin={false}
          gutterSize={isMobile ? 0 : 10}
          gutterAlign="center"
          snapOffset={30}
          dragInterval={1}
          direction="horizontal"
          cursor={isMobile ? "default" : "col-resize"}
          gutter={isMobile ?  undefined : gutter}
        >
          <Sidebar />
          <HomePageContent />
        </Split>
      </DataSourceProvider>
    </SidebarContext.Provider> 
  );
};

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
};

export default Home;
