import Split from "react-split";
import Main from "../components/Main";
import Sidebar from "../components/Sidebar";
// import { useState } from "react";

const Home = () => {
  // const [datasource, setDatasource] = useState([]);
  const gutter = () => {
    const gutterElement = document.createElement('div');
    gutterElement.className = `gutter bg-slate-200 hover:bg-blue-300 hover:cursor-col-resize`;
    return gutterElement;
  };
  return (
      <Split
        className="flex w-full h-full overflow-hidden"
        sizes={[20, 80]}
        minSize={100}
        expandToMin={false}
        gutterSize={5}
        gutterAlign="center"
        snapOffset={30}
        dragInterval={1}
        direction="horizontal"
        cursor="col-resize"
        gutter={gutter}
      >
        {/* <Sidebar datasource={datasource} setDatasource={setDatasource} /> */}
        <Sidebar />
        <Main />
      </Split>
  );
};

export default Home;
