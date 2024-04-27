import React, { useState } from 'react';
import './App.css';

interface Message {
  id: number;
  text: string;
  sender: string;
}

const getCookie = (name: string): string | null => {
  const cookieValue = document.cookie.split('; ')
    .find(cookie => cookie.startsWith(name + '='));

  return cookieValue ? cookieValue.split('=')[1] : null;
};

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [responseText, setResponseText] = useState('');

  const handleSendMessage = async () => {
    if (inputText.trim() !== '') {
      const newMessage: Message = {
        id: messages.length,
        text: inputText,
        sender: 'Me', // For simplicity, assuming the sender is "Me"
      };

      setMessages([...messages, newMessage]);
      setInputText('');

      try {
        const csrftoken = getCookie('csrftoken');
        if (!csrftoken) {
          throw new Error('CSRF token not found');
        }

        const response = await fetch('/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ message: inputText }),
          mode: 'same-origin',
        });

        if (!response.ok) {
          throw new Error('Failed to fetch');
        }

        const data = await response.json();
        setResponseText(data.response);
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h2>Chat History</h2>
        <ul>
          {messages.map((message) => (
            <li key={message.id}>
              <strong>{message.sender}:</strong> {message.text}
            </li>
          ))}
        </ul>
      </div>
      <div className="main-content">
        <h1>Chat Interface</h1>
        <div className="message-container">
          <ul className="message-list">
            {messages.map((message) => (
              <li key={message.id}>
                <strong>{message.sender}:</strong> {message.text}
              </li>
            ))}
          </ul>
        </div>
        <div className="input-container">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
        <div className="response-container">
          {responseText && <p><strong>Response:</strong> {responseText}</p>}
        </div>
      </div>
    </div>
  );
};

export default App;
