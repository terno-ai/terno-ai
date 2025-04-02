import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-chrome";
import "ace-builds/src-noconflict/ext-language_tools";
import { useContext, useEffect, useRef } from "react";
import { addCompleter } from 'ace-builds/src-noconflict/ext-language_tools';
import { DataSourceContext } from "./ui/datasource-context";

const SqlEditor = ({ ...props }) => {
  const { ds } = useContext(DataSourceContext);
  const customWords = [ds['name']]
  const editorRef = useRef<AceEditor | null>(null);
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

  useEffect(() => {
    const cursorLayer = document.querySelector(".ace_hidden-cursors");
    if (cursorLayer) {
      cursorLayer.classList.add("opacity-0");
    }
  }, []);
  
  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.editor.focus();
    }
  }, [props.value]); 

  return (
    <AceEditor
      ref={editorRef}
      className={props.className}
      mode="mysql"
      theme="chrome"
      name="sql-editor"
      // onLoad={onLoad}
      onChange={props.onChange}
      fontSize={14}
      showPrintMargin={true}
      showGutter={true}
      highlightActiveLine={true}
      value={props.value || ""}
      setOptions={{
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        showLineNumbers: true,
        tabSize: 2,
      }}
      width="100%"
      height="200px"
      style={{ backgroundColor: "#F2F2F2" }}        
    />
  );
};

export default SqlEditor;
