import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-github";
import "ace-builds/src-noconflict/ext-language_tools";
import { useContext, useEffect } from "react";
import { addCompleter } from 'ace-builds/src-noconflict/ext-language_tools';
import { DataSourceContext } from "./ui/datasource-context";

const SqlEditor = ({ ...props }) => {
  const { ds } = useContext(DataSourceContext);
  const customWords = [ds['name']]
  const customCompleter = {
    getCompletions: (_: any, __: any, ___: any, prefix: string, callback: (error: any, results: any[]) => void) => {
      if (prefix.length === 0) { callback(null, []); return }
      callback(null, customWords.map((word) => {
        return { name: word, value: word, score: 1000, meta: 'custom' }
      }));
    }
  };

  useEffect(() => {
    addCompleter(customCompleter);
  }, [ds]);

  return (
    <AceEditor
      className={props.className}
      mode="mysql"
      theme="github"
      name="sql-editor"
      // onLoad={onLoad}
      onChange={props.onChange}
      fontSize={14}
      showPrintMargin={true}
      showGutter={true}
      highlightActiveLine={true}
      value={props.value}
      setOptions={{
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        showLineNumbers: true,
        tabSize: 2,
      }}
      width="900px"
      height="200px"
    />
  );
};

export default SqlEditor;
