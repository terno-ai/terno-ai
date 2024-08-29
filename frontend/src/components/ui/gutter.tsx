const gutter = () => {
  const gutterElement = document.createElement('div');
  gutterElement.className = `relative bg-transparent hover:cursor-col-resize before:content-[''] before:absolute before:left-1/2 before:top-0 before:h-full before:w-px before:bg-slate-200 before:transform before:-translate-x-1/2 hover:before:bg-sky-300`
  return gutterElement;
};

export default gutter;