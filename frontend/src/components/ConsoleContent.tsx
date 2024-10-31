import PromptTemplateInput from "../components/PromptTemplateInput";
import { useContext, useState } from "react";
import SqlError from "../components/SqlError";
import terno from "../assets/terno.svg";
import PromptInput from "../components/PromptInput";
import { sendConsoleMessage } from "../utils/api";
import { DataSourceContext } from "./ui/datasource-context";
import useUserDetails from "../hooks/useUserDetails";
import { system_prompt, ai_prompt, human_prompt, available_vars } from "../utils/prompt_constants";
import { Link } from "react-router-dom";

const ConsoleContent = () => {
  const { ds } = useContext(DataSourceContext);
  const [user] = useUserDetails();
  const [systemPrompt, setSystemPrompt] = useState(system_prompt);
  const [assistantPrompt, setAssistantPrompt] = useState(ai_prompt);
  const [userPrompt, setUserPrompt] = useState(human_prompt);
  const [generatedPromptText, setGeneratedPromptText] = useState("");
  const [generatedQueryText, setGeneratedQueryText] = useState("");
  const [sqlError, setSqlError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    setLoading(true);
    setSqlError("");
    const response = await sendConsoleMessage(
      ds.id, systemPrompt, assistantPrompt,userPrompt);
    if (response["status"] == "success") {
      setGeneratedPromptText(response["generated_prompt"]);
      setGeneratedQueryText(response["generated_sql"]);
    } else {
      setSqlError(response["error"]);
    }
    setLoading(false);
  };

  return (
    <div className="min-w-[300px] h-screen inline-flex flex-col pb-10 px-[15px] overflow-y-auto">
      <div className="flex-1 min-w-[800px]">
        <div className="flex items-center justify-between text-xl p-5">
          <div className="inline-flex items-center">
            <img src={terno} className="logo h-[40px]" alt="Terno logo" />
            <p className="font-semibold">Terno AI - </p>
            <Link to={'/'} >Homepage</Link>
          </div>
          <div className="font-semibold">Developer Console</div>
          <div>{user.username}</div>
        </div>
        <div className="mt-10 max-w-4xl mx-auto">
          <div className="p-4 border rounded-md focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
            List of variables available: {available_vars}
          </div>
        </div>
        <PromptInput
          text="System"
          value={systemPrompt}
          setValue={setSystemPrompt}
          placeholder="Enter system instructions"
        />
        <PromptInput
          text="Assistant"
          value={assistantPrompt}
          setValue={setAssistantPrompt}
          placeholder="Enter assistant message..."
        />
        <PromptTemplateInput
          value={userPrompt}
          setValue={setUserPrompt}
          setGeneratedQueryText={setGeneratedQueryText}
          setSqlError={setSqlError}
          loading={loading}
          handleSendMessage={handleSendMessage}
        />
        <div className="mt-10 max-w-4xl mx-auto min-w-[800px] px-4">
          <div className="mt-4 mb-1 font-medium text-lg">Generated Prompt</div>
          <div className="flex overflow-scroll max-h-[200px] border px-4 rounded-md">
            <p>{generatedPromptText}</p>
          </div>
          <div className="mt-4 mb-1 font-medium text-lg">LLM Response</div>
          <div className="flex overflow-scroll max-h-[200px] border px-4 rounded-md">
              <p>{generatedQueryText}</p>
          </div>
        </div>
        <SqlError error={sqlError} />
      </div>
    </div>
  );
};

export default ConsoleContent;
