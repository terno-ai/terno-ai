import PromptTemplateInput from "../components/PromptTemplateInput";
import { Suspense, useContext, useState } from "react";
import SqlError from "../components/SqlError";
import terno from "../assets/terno.svg";
import SqlEditor from "../components/SqlEditor";
import PromptInput from "../components/PromptInput";
import { sendConsoleMessage } from "../utils/api";
import { DataSourceContext } from "./ui/datasource-context";

const ConsoleContent = () => {
  const { ds } = useContext(DataSourceContext);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [assistantPrompt, setAssistantPrompt] = useState("");
  const [userPrompt, setUserPrompt] = useState("");
  const [generatedPromptText, setGeneratedPromptText] = useState("");
  const [generatedQueryText, setGeneratedQueryText] = useState("");
  const [sqlError, setSqlError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    setLoading(true);
    setSqlError("");
    const response = await sendConsoleMessage(
      ds.id,
      systemPrompt,
      assistantPrompt,
      userPrompt
    );
    if (response["status"] == "success") {
      setGeneratedPromptText(response["generated_prompt"]);
      setGeneratedQueryText(response["generated_sql"]);
    } else {
      setSqlError(response["error"]);
    }
    setLoading(false);
  };

  return (
    <div className="h-full flex relative overflow-scroll">
      <div className="flex-1 min-w-[800px] pb-36 px-4 relative overflow-scroll">
        <div className="flex items-center justify-between text-xl p-5">
          <div className="inline-flex items-center">
            <img src={terno} className="logo h-[40px]" alt="Terno logo" />
            <p className="font-semibold">Terno AI</p>
          </div>
          <div className="font-semibold">Developer Console</div>
          <div>{"user.username"}</div>
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
        <div className="mt-10 max-w-4xl mx-auto min-w-[800px] pb-36 px-4">
          <div className="mt-4 mb-1 font-medium text-lg">Generated Prompt</div>
          <div>
            <p>{generatedPromptText}</p>
          </div>
          <div className="mt-4 mb-1 font-medium text-lg">Generated Query</div>
          <div className="flex align-center justify-center border focus-within:ring-1 focus-within:ring-sky-300">
            <Suspense fallback={<div className="p-5">Loading Editor...</div>}>
              <SqlEditor
                value={generatedQueryText}
                onChange={(value: string) => setGeneratedQueryText(value)}
              />
            </Suspense>
          </div>
        </div>
        <SqlError error={sqlError} />
      </div>
    </div>
  );
};

export default ConsoleContent;
