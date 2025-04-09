import PromptBox from "./PromptBox";
import { useState } from "react";
import Conversation from "./Conversation";

const ChatWindow = () => {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([]);

  const handleSend = (text: string) => {
    setMessages((prev) => [...prev, { role: "user", text }]);
    
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "bot", text: `Echo: ${text}` }]);
    }, 500);
  };

  return (
    <div className="flex flex-grow flex-col h-screen">
      
        {messages.length > 0 && <Conversation messages={messages} />}
        <PromptBox onSend={handleSend} />
    </div>
    
  );
};

export default ChatWindow;
