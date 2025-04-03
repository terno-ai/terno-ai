import { FaArrowUp } from "react-icons/fa"
import { useState, useEffect, useRef } from "react";

const placeholders = [
  "Explore the date",
  "Find XYZ in the data",
  "Manuplate the data",
  "Delete the data and add new tables to it"
];

const ChatWindow = () => {

  
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentPlaceholderIndex(prevIndex => 
        (prevIndex + 1) % placeholders.length
      );
    }, 1000);
    
    return () => clearInterval(intervalId);
  }, []);

  
  return (
 
        <div className="flex-1 h-screen bg-white flex flex-col justify-center items-center">
          <h1 className="text-black text-2xl font-semibold mb-6">
            What can I help with?
          </h1>
          <div className="w-5/6 max-w-3xl h-32 p-2 relative flex items-center bg-white text-black rounded-[2rem] p-4  border border-cyan-500 ">
            <textarea
              placeholder={placeholders[currentPlaceholderIndex]}
              className="flex-1 bg-transparent text-lg resize-none leading-tight pt-2 h-full focus:ring-0 focus:outline-none caret-black"
             // value={inputText}
              //onChange={(e) => setInputText(e.target.value)}
            />
            <button className=" text-gray-400 hover:text-black ml-3">
              <FaArrowUp size={20} />
            </button>
          </div>
        </div>
   
  );
};

export default ChatWindow;
