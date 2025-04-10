//import React from "react";

type Message = {
  role: "user" | "bot";
  text: string;
};

const Conversation = ({ messages }: { messages: Message[] }) => {
  return (
    <div className="w-full max-w-3xl mx-auto p-4 flex flex-col gap-4 bg-white">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`break-words rounded-xl px-4 py-2 max-w-[75%] ${
            msg.role === "user"
              ? "bg-black text-white self-end"
              : "bg-zinc-200 dark:bg-zinc-700 text-black dark:text-white self-start"
          }`}
        >
          {msg.text}
        </div>
      ))}
    </div>
  );
};

export default Conversation;
