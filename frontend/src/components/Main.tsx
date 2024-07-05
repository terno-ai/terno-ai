import "../index.css";
import { executeSQL, sendMessage } from "../utils/api";
import { lazy, Suspense, useState } from "react";
import RenderTable from "./RenderTable";
const SqlEditor = lazy(() => import("./SqlEditor"))
import SqlError from "./SqlError";

interface TableData {
  columns: string[];
  data: Record<string, string | number>[];
}

const Main = () => {
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
  return (
    <div className="flex-1 min-w-[800px] pb-36 px-4 relative overflow-scroll">
      <div className="flex items-center justify-between text-xl p-5 text-gray-600">
        <p className="font-semibold text-black">Terno AI</p>
      </div>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between gap-5 p-2.5 px-5 rounded-full bg-slate-100  hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
          <input
            type="text"
            placeholder="Enter a prompt here"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none p-2 text-lg focus:outline-none"
          />
          <p onClick={handleSendMessage} className="cursor-pointer">
            Send
          </p>
        </div>
        <div className="mt-10">
          <div className="mt-4 mb-1 font-medium text-lg">Generated Query</div>
          <div className="flex align-center justify-center border focus-within:ring-1 focus-within:ring-sky-300">
            <Suspense fallback={<div>Loading Editor...</div>}>
              <SqlEditor
                value={generatedQueryText}
                onChange={(value: string) => setGeneratedQueryText(value)}
              />
            </Suspense>
          </div>
          <div className="text-right">
            <button
              className="text-right inline-flex h-10 items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#1e2631,55%,#000103)] bg-[length:200%_100%] mt-4 px-10 font-medium text-white transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50"
              onClick={handleQueryExecute}
            >
              Execute
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
