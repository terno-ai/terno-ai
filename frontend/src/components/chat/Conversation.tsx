import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import terno from "../../assets/terno.svg";

type Message = {
  role: 'user' | 'bot';
  text: string;
  timestamp: string;
};

const Conversation = ({
  messages,
  promptBoxHeight,
  userHasScrolled,
}: {
  messages: Message[];
  promptBoxHeight: number;
  userHasScrolled: boolean;
}) => {
  const [renderedBotTexts, setRenderedBotTexts] = useState<string[]>([]);

  useEffect(() => {
    let i = 0;
    let msgIdx = 0;
    const typingSpeedMultiplier = 0.5;

    const botMessages = messages.filter((msg) => msg.role === 'bot');

    const interval = setInterval(() => {
      if (msgIdx >= botMessages.length) {
        clearInterval(interval);
        return;
      }

      const fullText = botMessages[msgIdx].text;
      const currentRendered = renderedBotTexts[msgIdx] || '';

      if (i <= fullText.length) {
        const updatedRendered = [...renderedBotTexts];
        updatedRendered[msgIdx] = fullText.slice(0, i);
        setRenderedBotTexts(updatedRendered);

        i++;
      } else {
        i = 0;
        msgIdx++;
      }
    }, 1 * typingSpeedMultiplier); //Typing Speed

    return () => clearInterval(interval);
  }, [messages]);

  const pairs: [Message?, string?, string?][] = [];
  let botIndex = 0;

  messages.forEach((msg) => {
    if (msg.role === 'user') {
      pairs.push([msg, undefined, undefined]);
    } else if (msg.role === 'bot') {
      pairs[pairs.length - 1][1] = renderedBotTexts[botIndex] ?? '';
      pairs[pairs.length - 1][2] = msg.timestamp;
      botIndex++;
    }
  });

  return (
    <div className="max-w-3xl mx-auto flex flex-col">
      {pairs.map(([userMsg, renderedBotMsg, botTimestamp], idx) => {
        const isLast = idx === pairs.length - 1;
        const minHeightStyle = isLast ? { minHeight: `calc(100vh - ${promptBoxHeight}px)` } : {};
        return (
          <div
            key={idx}
            style={minHeightStyle}
            className={`flex flex-col gap-4 ${isLast ? 'flex items-center' : ''}`}
          >
            {userMsg && (
              <div className="break-words px-4 py-2 bg-black text-white self-end rounded-xl max-w-[75%]">
                {userMsg.text}
              </div>
            )}
            {renderedBotMsg && (
              <div className="break-words px-4 py-2 text-black dark:text-white self-start rounded-xl w-full ">
                <div className="flex flex-row justify-between items-center mb-2">
                  <div className='flex items-center '>
                    <img src={terno} className="logo h-[25px]" alt="Terno logo" />
                    <p className="font-semibold">Terno AI</p>
                  </div>
                  <div className='flex items-center'>
                  <p className="text-sm text-gray-500 mt-1">{botTimestamp}</p>
                  </div>
                </div>
                <div>
                  <ReactMarkdown>{renderedBotMsg}</ReactMarkdown>
                  
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
