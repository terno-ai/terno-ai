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
    textareaRef.current.value = "";
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
      className={`flex flex-grow h-screen dark:bg-black ${hasSentMessage
        ? "flex-col justify-end items-center py-4 pb-28"
        : "flex-col justify-center items-center"
        }`}
    >
      {!hasSentMessage && (
        <h1 className="text-black dark:text-white text-3xl font-semibold mb-6 -mt-32">
          What can I help with?
        </h1>
      )}

      <div className="w-5/6 max-w-3xl h-40 relative flex flex-col bg-white dark:bg-zinc-900 text-black dark:text-white rounded-[2rem] p-4 border shadow-md">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            defaultValue={textareaRef.current?.value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholders[currentPlaceholderIndex]}
            className="w-full h-3/4 bg-transparent text-lg resize-none leading-tight px-4 pt-2 focus:ring-0 focus:outline-none caret-black dark:caret-white"
            rows={1}
          />
        </div>

        <div className="absolute bottom-1 left-4 right-4 flex justify-between items-center">
          <div className="flex gap-2">
            <button className="rounded-full border border-gray-300 dark:border-zinc-600 px-3 py-1 text-sm flex items-center gap-1 hover:bg-zinc-200 dark:hover:bg-zinc-800 transition">
              ➕
            </button>
          </div>
          <button
            onClick={handleSend}
            className={`p-2 rounded-full transition duration-200 ${isButtonActive
                ? "bg-black dark:bg-white text-white dark:text-black hover:opacity-90 cursor-pointer"
                : "bg-gray-400 text-white cursor-not-allowed opacity-50"
              }`}
            disabled={!isButtonActive}
          >
            <FaArrowUp size={20} />
          </button>
        </div>
      </div>



    </div>
  );
};

export default PromptBox;
