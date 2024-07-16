import Split from "react-split";
import Main from "../components/Main";
import Sidebar from "../components/Sidebar";
import { DataSourceProvider } from "../components/ui/datasource-context";

const Home = () => {
  const gutter = () => {
    const gutterElement = document.createElement('div');
    gutterElement.className = `relative bg-transparent hover:cursor-col-resize before:content-[''] before:absolute before:left-1/2 before:top-0 before:h-full before:w-px before:bg-slate-200 before:transform before:-translate-x-1/2 hover:before:bg-sky-300`
    return gutterElement;
  };
  return (
      <Split
        className="flex w-full h-full overflow-hidden"
        sizes={[20, 80]}
        minSize={100}
        expandToMin={false}
        gutterSize={10}
        gutterAlign="center"
        snapOffset={30}
        dragInterval={1}
        direction="horizontal"
        cursor="col-resize"
        gutter={gutter}
      >
        <DataSourceProvider>
          <Sidebar />
          <Main />
        </DataSourceProvider>
      </Split>
  );
};

export default Home;
