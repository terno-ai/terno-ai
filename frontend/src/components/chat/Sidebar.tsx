import { FaTimes } from "react-icons/fa";
import { useSidebar } from "./MainContent";


const Sidebar = () => {
  const { isSidebarOpen, toggleSidebar } = useSidebar();
  
  return (
    <>
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={toggleSidebar} 
        />
      )}

      <div
        className={`fixed inset-y-0 left-0 min-w-[300px] h-screen bg-white shadow-lg z-50 transition-transform duration-300 
          ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"} md:relative md:translate-x-0 md:flex`}
      >
        <button className="absolute top-4 right-4 md:hidden" onClick={toggleSidebar}>
          <FaTimes size={24} />
        </button>
          Sidebar
        <div className="w-full h-full flex-col py-5 px-4 overflow-y-auto">
        </div>
      </div>
    </>
  );
};

export default Sidebar;