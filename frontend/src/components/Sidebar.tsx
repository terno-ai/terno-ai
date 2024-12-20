import SchemaPane from "./SchemaPane";

const Sidebar = () => {
  return (
    <div className="min-w-[300px] h-screen hidden flex-col py-[25px] px-[15px] overflow-y-auto md:inline-flex">
      <SchemaPane />
    </div>
  );
};

export default Sidebar;
