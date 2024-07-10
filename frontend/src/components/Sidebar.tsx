import SchemaPane from "./SchemaPane";

const Sidebar = () => {
  return (
    <div className="min-w-[300px] h-screen inline-flex flex-col py-[25px] px-[15px] overflow-y-auto">
      <SchemaPane />
    </div>
  );
};

export default Sidebar;
