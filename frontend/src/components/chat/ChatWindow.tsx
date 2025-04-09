import PromptBox from "./PromptBox";
import Conversation from "./Conversation";
import { useState, useRef, useEffect  } from "react";
import { FaArrowDown } from "react-icons/fa"
import { WebSocketService, subscribeToChat, sendChatMessage } from "@/utils/api";

const ChatWindow = () => {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string; timestamp: string }[]>([]);
  const conversationRef = useRef<HTMLDivElement | null>(null);
  const promptBoxRef = useRef<HTMLDivElement | null>(null);
  const [promptHeight, setPromptHeight] = useState(0);
  const [userHasScrolled, setUserHasScrolled] = useState(false);

  useEffect(() => {
    const ws = WebSocketService.getInstance();
    ws.connect();

    const unsubscribe = subscribeToChat((data) => {
      if (data.message) {
        setMessages((prev) => [...prev, { role: "bot", text: data.message, timestamp: new Date().toLocaleTimeString() }]);
      }
    });

    return () => unsubscribe();
  }, []);

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", text, timestamp: new Date().toLocaleTimeString() }]);
    sendChatMessage(text);
  };

  useEffect(() => {
    if (!promptBoxRef.current) return;
  
    const observer = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setPromptHeight(entry.contentRect.height);
      }
    });
  
    observer.observe(promptBoxRef.current);
  
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTo({
        top: conversationRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);
  
  useEffect(() => {
    const el = conversationRef.current;
    if (!el) return;
  
    const handleScroll = () => {
      const nearBottom =
        el.scrollHeight - el.scrollTop - el.clientHeight < 20;
      setUserHasScrolled(!nearBottom);
    };
  
    el.addEventListener("scroll", handleScroll);
    return () => el.removeEventListener("scroll", handleScroll);
  }, []);
  
  // useLayoutEffect(() => {
  //   const el = conversationRef.current;
  //   if (!el || userHasScrolled) return;

  //   el.scrollTop = el.scrollHeight;
  // }, [messages]);
  
  const scrollToBottom = () => {
    const el = conversationRef.current;
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  };
  

  return (
    <div className="flex flex-col w-full">
    {messages.length > 0 && (
      <div className="relative flex-grow min-h-0">
        <div
          ref={conversationRef}
          className="overflow-y-auto h-full"
        >
          <Conversation
            messages={messages}
            promptBoxHeight={promptHeight}
          />
        </div>
        {userHasScrolled && (
          <button
            onClick={scrollToBottom}
            className="absolute bottom-[2px] left-1/2 transform -translate-x-1/2 z-50 p-2 rounded-full transition bg-gray-400 text-white"
          >
            <FaArrowDown size={20} />
          </button>
        )}
      </div>
    )}
      

      <div ref={promptBoxRef} className="">
        <PromptBox onSend={handleSend} />
      </div>
    </div>


  );
};

export default ChatWindow;
