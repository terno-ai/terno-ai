import "../index.css";
import { executeSQL, exportSQLResult, sendMessage } from "../utils/api";
import { lazy, Suspense, useContext, useRef, useState, useTransition, useEffect } from "react";
import RenderTable from "./RenderTable";
import SqlError from "./SqlError";
import { FaCopy, FaDownload, FaPlay, FaArrowUp, FaArrowDown } from "react-icons/fa6";
import { DataSourceContext } from "./ui/datasource-context";
import PaginatedList from "./TablePagination";
import Navbar from "./Navbar";



interface TableData {
  columns: string[];
  data: Record<string, string | number>[];
  row_count: number;
  total_pages: number;
}

const HomePageContent = () => {
  const { ds } = useContext(DataSourceContext);
  //const [inputText, setInputText] = useState("");
  const [generatedQueryText, setGeneratedQueryText] = useState("");
  const [tableData, setTableData] = useState<TableData>({
    columns: [], data: [], row_count: 0, total_pages: 0
  });
  const [sqlError, setSqlError] = useState("");
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [height, setHeight] = useState('auto');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [loadPaginate, setLoadPaginate] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPending, startTransition] = useTransition();
  const SqlEditor = lazy(() => import("./SqlEditor"));
  const inputRef = useRef("");

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const toggleExpand = () => {
    startTransition(() => {
      setIsExpanded((prev) => !prev);
    });
  };
  const expandOnly = () => {
    startTransition(() => {
      setIsExpanded(true);
    });
  };
  const handleSendMessage = async () => {
    setLoading(true);
    setSqlError("");
    const response = await sendMessage(inputRef.current, ds.id);
    if (response["status"] == "success") {
      setGeneratedQueryText(response["generated_sql"]);
    } else {
      setSqlError(response["error"]);
    }
    setLoading(false);
  };

  const handleQueryExecute = async (page: number) => {
    setLoading(true);
    setSqlError("");
    setTableData({ columns: [], data: [], row_count: 0, total_pages: 0 });
    const response = await executeSQL(generatedQueryText, ds.id, page);
    if (response["status"] == "success") {
      setTableData(response["table_data"]);
      setLoadPaginate(true);
    } else {
      setSqlError(response["error"]);
    }
    setLoading(false);
  };

  const handleQueryResultExport = async () => {
    setExporting(true);
    await exportSQLResult(generatedQueryText, ds.id);
    setExporting(false);
  };

  const handleInput = () => {
    if (textareaRef.current) {
      const content = textareaRef.current.value;

      if (content.length === 0) {
        setHeight('auto');
      }
      const currentScrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = 5 * parseFloat(getComputedStyle(textareaRef.current).lineHeight || '1.5');
      const newHeight = Math.min(currentScrollHeight, maxHeight);

      if (`${newHeight}px` !== height) {
        setHeight(`${newHeight}px`);
      }
    }
  };

  const [isCopied, setIsCopied] = useState(false);
  const handleCopy = async () => {
    const tableString = `${tableData.columns.join("\t")}
      ${tableData.data
        .map((row) =>
          tableData.columns
            .map((col) => `${row[col]}`).join("\t"))
        .join("\n")}`;
    try {
      await navigator.clipboard.writeText(tableString);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy text: ", error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      console.log("Coming Here!!")
      e.preventDefault();
      if(!inputRef.current.trim()) return;
      handleSendMessage();
      expandOnly();
    }
  };

  return (
    <div className=" max-h-screen inline-flex flex-col flex-grow pb-10 px-[15px] overflow-y-auto ">
      <Navbar />
      <div className="w-full max-w-4xl mx-auto">
        <div className="flex flex-grow items-center w-full border-2 gap-5 p-2.5 px-5 rounded-md hover:drop-shadow-sm border-gray-400 focus-within:ring-2 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none focus-within:border-transparent">
          <textarea
            onInput={handleInput}
            ref={textareaRef}
            placeholder="Enter a prompt here"
            defaultValue={inputRef.current}
            onChange={(e) => (inputRef.current = e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            className="flex-grow w-full min-w-0 p-2 bg-transparent border-none outline-none rounded-md resize-none overflow-y-auto sm:text-sm md:text-base "
            style={{ height }}
          />

        </div>
        <div className="flex flex-row align-center justify-end">
          <button
            className="inline-flex h-10 items-center justify-center rounded-md border bg-cyan-500 hover:bg-cyan-600 mt-4 px-10 font-medium text-white"
            onClick={() => {
              handleSendMessage();
              expandOnly();
            }}
            disabled={loading || isPending}
          >
            {/* {isPending ? "Wait" : "Run"} */}
            {loading ? "Wait" : "Run"}
            <FaPlay className="ml-1" />
          </button>
        </div>
        <div className="my-2 flex flex-row gap-2">
          <button
            className="px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-full"
          >
            Show me purchases made by customers in canada
          </button>
          <button
            className="px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-full"
          >
            Show me albums by artist
          </button>
          <button
            className="px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-full"
          >
            Rock music by artist
          </button>
        </div>
        <div className="mt-10">
          <div className="mt-6 w-full max-w-4xl mx-auto">
            <button
              className="flex items-center justify-between w-full px-4 py-2 text-lg font-medium bg-gray-100 border rounded-md hover:bg-gray-200"
              onClick={toggleExpand}
            >
              Generated Query
              {isExpanded ? <FaArrowUp /> : <FaArrowDown />}
            </button>
          </div>
          {isExpanded && (<div className="w-full max-w-4xl mx-auto transition-all duration-300 ease-in-out">
            <div className="flex items-center justify-center border focus-within:ring-1 focus-within:ring-sky-300">
              <Suspense fallback={<div className="p-5">Loading Editor...</div>}>
                <SqlEditor
                  value={generatedQueryText}
                  onChange={(value: string) => setGeneratedQueryText(value)}
                />
              </Suspense>
            </div>

            <div className="flex flex-row align-center justify-end">
              <button
                className="text-right inline-flex h-10 items-center justify-center rounded-md border bg-gray-500 hover:bg-cyan-600 mt-4 px-10 font-medium text-white transition-colors hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 focus:ring-offset-slate-50"
                onClick={() => handleQueryExecute(1)}
                disabled={loading}
              >
                {loading ? 'Wait' : 'Execute'}
                <FaPlay className="ml-1" />
              </button>
            </div>
          </div>)}

        </div>
        <div>
          <div className="flex items-center justify-between">
            <div className=" mt-6 font-medium text-lg text-left">Result</div>
            {tableData.row_count > 0 &&
              <div className=" mb-1 flex space-x-2 items-center justify-end">
                <button
                  className="inline-flex h-9 items-center rounded-md bg-sky-50 hover:bg-sky-200 mt-4 px-10 font-medium text-cyan-600 hover:opacity-100"
                  onClick={() => handleQueryResultExport()}
                >
                  {exporting ? 'Exporting' : 'Export'}
                  <FaDownload className="ml-1" />
                </button>
                <button
                  className="inline-flex h-9 items-center rounded-md bg-sky-50 hover:bg-sky-200 mt-4 px-10 font-medium text-cyan-600 hover:opacity-100"
                  onClick={() => handleCopy()}
                >
                  {isCopied ? 'Copied' : 'Copy'}
                  <FaCopy className="ml-1" />
                </button>
              </div>
            }
          </div>
        </div>
        <div className="max-h-[200px]">
          <SqlError error={sqlError} />
          <RenderTable columns={tableData.columns} data={tableData.data} />
          {loadPaginate && !loading &&
            <><PaginatedList totalPages={tableData.total_pages} onSelect={handleQueryExecute} />
              <div className="text-center m-2">{tableData.row_count} Rows</div>
            </>}
        </div>
      </div>
    </div>
  );
};

export default HomePageContent;
