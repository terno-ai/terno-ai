import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

type Message = {
  role: "user" | "bot";
  text: string;
  timestamp: string;
};

const Conversation = ({
  messages,
  promptBoxHeight,
}: {
  messages: Message[];
  promptBoxHeight: number;
}) => {
  const [renderedBotMessages, setRenderedBotMessages] = useState<string[]>([]);

  useEffect(() => {
    const botMessages: string[] = messages
      .filter((msg) => msg.role === 'bot')
      .map((msg) => msg.text);

    const chunkedMessages: string[] = [];
    let currentChunk = '';

    botMessages.forEach((message) => {
      const words = message.split(' ');
      words.forEach((word) => {
        currentChunk += word + ' ';
        chunkedMessages.push(currentChunk.trim());
      });
    });

    setRenderedBotMessages(chunkedMessages);
  }, [messages]);

  // Group messages in pairs: [user, bot]
  const pairs: [Message?, string?, string?][] = [];
  let botMessageIndex = 0;

  messages.forEach((msg) => {
    if (msg.role === 'user') {
      pairs.push([msg, undefined, undefined]);
    } else if (msg.role === 'bot') {
      pairs[pairs.length - 1][1] = renderedBotMessages[botMessageIndex];
      pairs[pairs.length - 1][2] = msg.timestamp;
      botMessageIndex++;
    }
  });

  return (
    <div className="max-w-3xl mx-auto flex flex-col ">
      {pairs.map(([userMsg, renderedBotMsg, botTimestamp], idx) => {
        const isLast = idx === pairs.length - 1;
        const minHeightStyle = isLast ? { minHeight: `calc(100vh - ${promptBoxHeight}px)` } : {};
        return (
          <div key={idx} style={minHeightStyle} className={`flex flex-col gap-4 ${isLast ? 'flex items-center' : ''}`}>
            {userMsg && (
              <div className="break-words px-4 py-2 bg-black text-white self-end rounded-xl max-w-[75%]">
                {userMsg.text}
              </div>
            )}
            {renderedBotMsg && (
              <div className="break-words px-4 py-2 text-black dark:text-white self-start rounded-xl max-w-[103%] flex items-start">
                <span role="img" aria-label="bot-icon" className="mr-2">🤖</span>
                <div>
                  <ReactMarkdown>{renderedBotMsg}</ReactMarkdown>
                  <p className="text-sm text-gray-500 mt-1">{botTimestamp}</p>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Conversation;