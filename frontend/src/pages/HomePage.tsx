import Split from "react-split";
import HomePageContent from "../components/HomePageContent";
import Sidebar from "../components/Sidebar";
import { DataSourceProvider } from "../components/ui/datasource-context";
import gutter from "../components/ui/gutter";
import Hotjar from "@hotjar/browser";

const Home = () => {
  const siteId = 5244049;
  const hotjarVersion = 6;

  Hotjar.init(siteId, hotjarVersion);

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
        <HomePageContent />
      </Split>
    </DataSourceProvider>
  );
};

export default Home;
