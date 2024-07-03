import Split from "react-split";
import Main from "../components/Main";
import Sidebar from "../components/Sidebar";

const Home = () => {
  return (
      <Split
        className="flex w-full"
        sizes={[20, 80]}
        minSize={100}
        expandToMin={false}
        gutterSize={10}
        gutterAlign="center"
        snapOffset={30}
        dragInterval={1}
        direction="horizontal"
        cursor="col-resize"
      >
        <Sidebar />
        <Main />
      </Split>
  );
};

export default Home;
