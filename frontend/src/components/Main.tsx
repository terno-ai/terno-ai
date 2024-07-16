import "../index.css";
import { executeSQL, sendMessage } from "../utils/api";
import { KeyboardEvent, lazy, Suspense, useContext, useState } from "react";
import RenderTable from "./RenderTable";
const SqlEditor = lazy(() => import("./SqlEditor"))
import SqlError from "./SqlError";
import { FaArrowRight, FaPlay } from "react-icons/fa6";
import terno from "../assets/terno.svg";
import { DataSourceContext } from "./ui/datasource-context";

interface TableData {
  columns: string[];
  data: Record<string, string | number>[];
}

const Main = () => {
  const { ds } = useContext(DataSourceContext);
  const [inputText, setInputText] = useState("");
  const [generatedQueryText, setGeneratedQueryText] = useState("");
  const [tableData, setTableData] = useState<TableData>({
    columns: [],
    data: [],
  });
  const [sqlError, setSqlError] = useState("");

  const handleSendMessage = async () => {
    const response = await sendMessage(inputText);
    setGeneratedQueryText(String(response));
  };
  const handleQueryExecute = async () => {
    setSqlError("");
    setTableData({ columns: [], data: [] });
    const response = await executeSQL(generatedQueryText);
    if (response["status"] == "success") {
      setTableData(response["table_data"]);
    } else {
      setSqlError(response["error"]);
    }
  };
  const handleKeyDownSend = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.code === 'Enter') {
      handleSendMessage();
    }
  };
  return (
    <div className="flex-1 min-w-[800px] pb-36 px-4 relative overflow-scroll">
      <div className="flex items-center justify-between text-xl p-5">
        <div className="inline-flex items-center">
          <img src={terno} className="logo h-[40px]" alt="Terno logo" />
          <p className="font-semibold">Terno AI</p>
        </div>
        <div className="font-semibold">{ds.name}</div>
        <div>Profile</div>
      </div>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between gap-5 p-2.5 px-5 rounded-full bg-slate-100  hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
          <input
            type="text"
            placeholder="Enter a prompt here"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDownSend}
            className="flex-1 bg-transparent border-none outline-none p-2 text-lg focus:outline-none"
          />
          <div onClick={handleSendMessage} className="p-2 border text-cyan-500 border-cyan-500 rounded-full items-center justify-center cursor-pointer hover:bg-gray-200">
            <FaArrowRight />
          </div>
        </div>
        <div className="mt-10">
          <div className="mt-4 mb-1 font-medium text-lg">Generated Query</div>
          <div className="flex align-center justify-center border focus-within:ring-1 focus-within:ring-sky-300">
            <Suspense fallback={<div className="p-5">Loading Editor...</div>}>
              <SqlEditor
                value={generatedQueryText}
                onChange={(value: string) => setGeneratedQueryText(value)}
              />
            </Suspense>
          </div>
          <div className="text-right">
            <button
              className="text-right inline-flex h-10 items-center justify-center rounded-md border bg-cyan-500 hover:bg-cyan-600 mt-4 px-10 font-medium text-white transition-colors hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 focus:ring-offset-slate-50"
              onClick={handleQueryExecute}
            >
              Execute
              <FaPlay className="ml-1" />
            </button>
          </div>
        </div>
        <div>
          <div className="mt-10 font-medium text-lg">Result</div>
          <div className="max-h-[200px]">
            <SqlError error={sqlError} />
            <RenderTable columns={tableData.columns} data={tableData.data} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Main;
