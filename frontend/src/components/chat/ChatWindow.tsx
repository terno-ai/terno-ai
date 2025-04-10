import PromptBox from "./PromptBox";
import Conversation from "./Conversation";
import { useState } from "react";
import { agentResponse } from "@/utils/api";

const ChatWindow = () => {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([]);

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", text }]);

    await agentResponse(text, (data) => {
      console.log('Received message:', data);
      if (data.message) {
        setMessages((prev) => [...prev, { role: "bot", text: data.message }]);
      }
    });

    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "bot", text: `Echo: ${text}` }]);
    }, 500);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden">
      {messages.length > 0 &&
        <div className="flex flex-grow inset-0 overflow-y-auto pb-28 px-4 pt-4 [scrollbar-gutter:stable]">
          <Conversation messages={messages} />
        </div>
      }

      <div className="">
        <PromptBox onSend={handleSend} />
      </div>
    </div>

    
  );
};

export default ChatWindow;
