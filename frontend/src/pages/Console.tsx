import Split from "react-split";
import Sidebar from "../components/Sidebar";
import { DataSourceProvider } from "../components/ui/datasource-context";
import gutter from "../components/ui/gutter";
import ConsoleContent from "../components/ConsoleContent";

const Console = () => {
  return (
    <DataSourceProvider>
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
        <Sidebar />
        <ConsoleContent />
      </Split>
    </DataSourceProvider>
  );
};

export default Console;
