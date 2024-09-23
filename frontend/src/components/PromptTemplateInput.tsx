import { FaArrowRight } from "react-icons/fa6";

const PromptTemplateInput = ({...props}) => {
  return (
    <div className="mt-10 max-w-4xl mx-auto">
      <div className="flex items-center justify-between gap-5 p-2.5 px-5 rounded-full bg-slate-100  hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
        <input
          type="text"
          placeholder="Enter a prompt here"
          value={props.value}
          onChange={(e) => props.setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && props.handleSendMessage()}
          className="flex-1 bg-transparent border-none outline-none p-2 text-lg focus:outline-none"
        />
        <button
          className="p-2 border text-cyan-500 border-cyan-500 rounded-full items-center justify-center hover:bg-gray-200"
          onClick={props.handleSendMessage}
          disabled={props.loading}
        >
          {props.loading ? 'Wait': <FaArrowRight />}
        </button>
      </div>
    </div>
  )
}

export default PromptTemplateInput