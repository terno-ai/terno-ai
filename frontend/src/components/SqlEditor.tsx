import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-github";
import "ace-builds/src-noconflict/ext-language_tools"

const SqlEditor = ({...props}) => {
  return (
    <AceEditor
        className={props.className}
        mode="mysql"
        theme="xcode"
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
  )
}

export default SqlEditor