import React, { useState } from 'react';

const Settings: React.FC = () => {
  const [apiKey, setApiKey] = useState(''); // State to hold the API key
  const [newApiKey, setNewApiKey] = useState(''); // State to hold the new API key input value

  // Function to handle form submission
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Update the API key with the new value
    setApiKey(newApiKey);
    // Clear the input field
    setNewApiKey('');
  };

  return (
    <div>
      <h1>Settings</h1>
      <form onSubmit={handleSubmit}>
        <label>
          API Key:
          <input
            type="text"
            value={newApiKey}
            onChange={(e) => setNewApiKey(e.target.value)}
          />
        </label>
        <button type="submit">Update</button>
      </form>
      <div>
        <h2>Current API Key:</h2>
        <p>{apiKey}</p>
      </div>
    </div>
  );
};

export default Settings;