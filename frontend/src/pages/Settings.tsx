import React, { useState } from "react";

const Settings = () => {
  const [apiKey, setApiKey] = useState("");
  const [newApiKey, setNewApiKey] = useState("");

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setApiKey(newApiKey);
    setNewApiKey("");
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
