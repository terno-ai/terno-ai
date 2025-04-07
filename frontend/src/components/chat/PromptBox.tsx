import { FaArrowUp } from "react-icons/fa"
import { useState, useEffect, useRef } from "react";

const placeholders = [
  "Explore the data",
  "Find XYZ in the data",
  "Manipulate the data",
  "Delete the data and add new tables to it"
];

const PromptBox = () => {
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);
  const textareaRef = useRef<{ value: string; element: HTMLTextAreaElement | null }>({
    value: "", 
    element: null
  });
  const [isButtonActive, setIsButtonActive] = useState(false);

  const handleInputChange = () => {
    if (!textareaRef.current) return; 
    const value = String(textareaRef.current.value); 
    setIsButtonActive(value.trim().length > 0);
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentPlaceholderIndex(prevIndex => 
        (prevIndex + 1) % placeholders.length
      );
    }, 2000);
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="flex flex-grow h-screen bg-white dark:bg-black flex-col justify-center items-center">
      <h1 className="text-black dark:text-white text-3xl font-semibold mb-6 -mt-32">
        What can I help with?
      </h1>
      <div className="w-5/6 max-w-3xl h-32 relative flex bg-white dark:bg-zinc-900 text-black dark:text-white rounded-[2rem] p-4 border shadow-md">
        <textarea
          placeholder={placeholders[currentPlaceholderIndex]}
          className="flex-grow bg-transparent text-lg resize-none leading-tight pt-2 pr-12 pl-4 h-full focus:ring-0 focus:outline-none caret-black dark:caret-white"
          ref={textareaRef}
          onChange={handleInputChange}
        />
        <button
          className={`absolute right-[10px] top-1/2 transform -translate-y-1/2 p-3 rounded-full shadow-[0px_2px_6px_#000000] transition duration-200 ${
            isButtonActive
              ? "bg-black dark:bg-white text-white dark:text-black hover:opacity-90 cursor-pointer"
              : "bg-gray-400 text-white cursor-not-allowed opacity-50"
          }`}
          disabled={!isButtonActive}
        >
          <FaArrowUp size={20} />
        </button>
      </div>
    </div>
  );
};

export default PromptBox;
