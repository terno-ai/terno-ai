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
    if (!textareaRef.current?.value.trim()) return;
    setHasSentMessage(true);
    onSend(textareaRef.current.value);
    textareaRef.current.value = "";
    textareaRef.current.style.height = "auto";
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
      className={`flex flex-col dark:bg-black ${hasSentMessage
        ? "flex-col justify-end items-center py-4 pb-24"
        : "justify-center min-h-screen items-center"
        }`}
    >
      {!hasSentMessage && (
        <h1 className="text-black dark:text-white text-3xl font-semibold mb-6 -mt-32">
          What can I help with?
        </h1>
      )}

      <div className="w-5/6 max-w-3xl bg-white dark:bg-zinc-900 text-black dark:text-white rounded-[2rem] p-4 border shadow-md flex flex-col">
        <div className="flex flex-col-reverse">
          <div className="flex justify-between items-center mt-2">
            <div className="flex gap-2">

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
          <textarea
            ref={textareaRef}
            onChange={() => {
              handleInputChange();
              if (textareaRef.current) {
                textareaRef.current.style.height = "auto";
                //Maximum 6 lines before scroll bar triggers
                const maxHeight = 6 * 24;
                textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, maxHeight)}px`;
              }
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholders[currentPlaceholderIndex]}
            className="w-full text-lg resize-none leading-tight px-4 pt-2 focus:ring-0 focus:outline-none caret-black dark:caret-white max-h-[144px] overflow-y-auto bg-transparent"
            rows={1}
          />
        </div>
      </div>




    </div>
  );
};

export default PromptBox;
