import { FaArrowUp } from "react-icons/fa"
import { useState, useEffect, useRef } from "react";

const placeholders = [
  "Explore the data",
  "Find XYZ in the data",
  "Manipulate the data",
  "Delete the data and add new tables to it"
];

const PromptBox = ({ onSend }: { onSend: (text: string) => void }) => {
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);
  const [hasSentMessage, setHasSentMessage] = useState(false);
  //const [inputValue, setInputValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

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

  const handleSend = () => {
    console.log("Coming in handleSend 1", textareaRef)
    if (!textareaRef.current?.value.trim()) return;
    console.log("Coming in handleSend 2")
    setHasSentMessage(true);
    onSend(textareaRef.current.value);
    //setInputValue("");
    setIsButtonActive(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className={`flex flex-grow h-screen dark:bg-black ${
        hasSentMessage
          ? "flex-col justify-end items-center py-4 pb-28"
          : "flex-col justify-center items-center"
      }`}
    >
      {!hasSentMessage && (
        <h1 className="text-black dark:text-white text-3xl font-semibold mb-6 -mt-32">
          What can I help with?
        </h1>
      )}
      <div className="w-5/6 max-w-3xl h-32 relative flex bg-white dark:bg-zinc-900 text-black dark:text-white rounded-[2rem] p-4 border shadow-md">
        <textarea
          ref={textareaRef}
          defaultValue={textareaRef.current?.value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholders[currentPlaceholderIndex]}
          className="flex-grow bg-transparent text-lg resize-none leading-tight pt-2 pr-12 pl-4 h-full focus:ring-0 focus:outline-none caret-black dark:caret-white"
          rows={1}
        />
        <button
          onClick={handleSend}
          className={`absolute right-[10px] top-1/2 transform -translate-y-1/2 p-3 rounded-full transition duration-200 ${
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
