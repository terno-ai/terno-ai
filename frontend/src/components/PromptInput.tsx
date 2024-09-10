const PromptInput = ({...props}) => {
  return (
    <div className="mt-10 max-w-4xl mx-auto">
      <div className="p-4 border rounded-md focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
        <div className="font-medium mb-2">
          {props.text}
        </div>
        <div className="w-full">
          <input
            value={props.value}
            placeholder={props.placeholder}
            onChange={(e) => props.setValue(e.target.value)}
            className="w-full focus:outline-none"
          />
        </div>
      </div>
    </div>
  )
}

export default PromptInput