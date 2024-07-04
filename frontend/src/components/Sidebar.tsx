import SchemaPane from "./SchemaPane";

const Sidebar = () => {
  return (
    <div className="min-w-[300px] inline-flex flex-col bg-slate-100 py-[25px] px-[15px] overflow-y-auto">
      <div className="w-full justify-center mt-[50px] flex items-center gap-[10px] py-[10px] px-[15px] bg-slate-300 rounded-[50px] text-md slate-500 cursor-pointer">
        <p>New Chat</p>
      </div>
      <div className="flex flex-col">
        <p className="mt-8 mb-1">Recent</p>
        <div className="flex items-start rounded-full text-[#282828] cursor-pointer hover:bg-[#e2e6eb]">
          <p>Last query</p>
        </div>
      </div>
      <SchemaPane />
    </div>
  );
};

export default Sidebar;
