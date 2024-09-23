import Split from "react-split";
import Sidebar from "../components/Sidebar";
import { DataSourceProvider } from "../components/ui/datasource-context";
import gutter from "../components/ui/gutter";
import ConsoleContent from "../components/ConsoleContent";

const Console = () => {
  return (
    <DataSourceProvider>
      <Split
        className="flex w-full h-full overflow-hidden"
        sizes={[20, 80]}
        minSize={100}
        expandToMin={false}
        gutterSize={10}
        gutterAlign="center"
        snapOffset={30}
        dragInterval={1}
        direction="horizontal"
        cursor="col-resize"
        gutter={gutter}
      >
<<<<<<< HEAD
          <Sidebar />
            <div className="flex-1 min-w-[800px] pb-36 px-4 relative overflow-scroll">
              <div className="flex items-center justify-between text-xl p-5">
            <div className="inline-flex items-center">
              <img src={terno} className="logo h-[40px]" alt="Terno logo" />
              <p className="font-semibold">Terno AI</p>
            </div>
            <div className="font-semibold">{ds.name}</div>
              <div>{'user.username'}</div>
            </div>
            <PromptTemplateInput
              value={inputPrompt}
              setValue={setInputPrompt}
              setGeneratedQueryText={setGeneratedQueryText}
              setSqlError={setSqlError}
            />
            <div className="mt-2 max-w-4xl mx-auto min-w-[800px] px-4">
              Available variables are: dialect_name, dialect_version, db_schema. Use curly braces for variables.
            </div>
            <div className="mt-10 max-w-4xl mx-auto min-w-[800px] pb-36 px-4">
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
=======
        <Sidebar />
        <ConsoleContent />
>>>>>>> b80840426b4b50ead46357f675eac3419f51341d
      </Split>
    </DataSourceProvider>
  );
};

export default Console;
