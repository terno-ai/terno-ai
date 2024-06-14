const Sidebar = () => {
  return (
    <div className='min-h-screen inline-flex flex-col justify-between bg-slate-100 py-[25px] px-[15px]'>
      <div className='top'>
        <div className=" mt-[50px] inline-flex items-center gap-[10px] py-[10px] px-[15px] bg-slate-300 rounded-[50px] text-md slate-500 cursor-pointer">
          <p>New Chat</p>
        </div>
        <div className='flex flex-col'>
          <p className='mt-8 mb-5'>Recent</p>
          <div className="flex items-start gap-2.5 p-2 pr-10 rounded-full text-[#282828] cursor-pointer hover:bg-[#e2e6eb]">
            <p>What is react</p>
          </div>
        </div>
      </div>
      <div className='flex flex-col'>
        <div className="flex items-start gap-2.5 p-2 pr-10 rounded-full text-[#282828] cursor-pointer hover:bg-[#e2e6eb]">
          <img className='w-[20px]' />
          <p>Help</p>
        </div>
        <div className="flex items-start gap-2.5 p-2 pr-10 rounded-full text-[#282828] cursor-pointer hover:bg-[#e2e6eb]">
          <img className='w-[20px]' />
          <p>Activity</p>
        </div>
        <div className="flex items-start gap-2.5 p-2 pr-10 rounded-full text-[#282828] cursor-pointer hover:bg-[#e2e6eb]">
          <img className='w-[20px]' />
          <p>Settings</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar