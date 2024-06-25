import '../index.css'
import { executeSQL, sendMessage } from '../utils/api'
import { useState } from 'react'
import RenderTable from './RenderTable'
import DropDownMenu from './DropDownMenu';


interface TableData {
    columns: string[];
    data: Record<string, string | number>[];
}

const Main = () => {
    const [inputText, setInputText] = useState('');
    const [generatedQueryText, setGeneratedQueryText] = useState('');
    const [tableData, setTableData] = useState<TableData>({ columns: [], data: [] });

    const handleSendMessage = async () => {
        const response = await sendMessage(inputText);
        setGeneratedQueryText(String(response));
    }
    const handleQueryExecute = async () => {
        const response = await executeSQL(generatedQueryText);
        setTableData(response);
    }
  return (
    <div className="main flex-1 min-h-screen pb-36 relative overflow-scroll">
        <div className="nav flex items-center justify-between text-xl p-5 text-gray-600">
            <p className='font-semibold text-black'>Terno AI</p>
            <DropDownMenu />
        </div>
        <div className="main-container max-w-4xl mx-auto">
            <div className="search-box flex items-center justify-between gap-5 p-2.5 px-5 rounded-full bg-slate-100 drop-shadow-md hover:drop-shadow-lg">
                <input
                    type='text'
                    placeholder='Enter a prompt here'
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className='flex-1 bg-transparent border-none outline-none p-2 text-lg'
                />
                <p onClick={handleSendMessage} className='cursor-pointer'>Send</p>
            </div>
            <div className='mt-10 generated-query'>
                <div className='mt-4 mb-1 font-medium text-lg'>Generated Query</div>
                <div className="flex align-center justify-center bg-slate-100 rounded-md px-1">
                    <input
                        type='text'
                        className='flex-1 bg-transparent p-4 outline-none'
                        value={generatedQueryText}
                        onChange={(e) => setGeneratedQueryText(e.target.value)}
                    />
                </div>
                <div className='text-right'>
                    <button
                        className="text-right inline-flex h-12 items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#1e2631,55%,#000103)] bg-[length:200%_100%] mt-4 px-6 font-medium text-white transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50"
                        onClick={handleQueryExecute}
                    >
                        Execute
                    </button>
                </div>
            </div>
            <div>
                <div className='mt-10 font-medium text-lg'>Result</div>
                <div>
                    <RenderTable columns={tableData.columns} data={tableData.data} />
                </div>
            </div>
        </div>
    </div>
  )
}

export default Main