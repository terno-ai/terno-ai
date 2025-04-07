import { useContext, useState } from "react";
import terno from "../assets/terno.svg";
import useUserDetails from "../hooks/useUserDetails";
import { DataSourceContext } from "./ui/datasource-context";
import { logout } from "../utils/api";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/DropdownMenu";
import { ChevronDown, LogOut } from "lucide-react";
import { FaBars } from "react-icons/fa";
import { FaArrowUpRightFromSquare  } from "react-icons/fa6";
import { useSidebar } from "./chat/MainContent";
import { ModeToggle } from "./chat/mode-toggle";

const Navbar = () => {
  const { toggleSidebar } = useSidebar(); 
  const { toggleSidebar } = useSidebar(); 
  const [user] = useUserDetails();
  const { ds } = useContext(DataSourceContext);
  const [response, setResponse] = useState({ fetching: false, content: null });

  const submit = () => {
    setResponse({ ...response, fetching: true });
    logout()
      .then((content) => {
        setResponse((r) => {
          return { ...r, content };
        });
      })
      .catch((e) => {
        console.error(e);
        window.alert(e);
      })
      .then(() => {
        setResponse((r) => {
          return { ...r, fetching: false };
        });
      });
  };

  if (response.content) {
    window.location.href = 'https://app.terno.ai';
  }

  return (
    <div className="flex items-center justify-between text-xl p-5 pl-2">
      <div className="flex items-center space-x-3">  
        <button
          className="md:hidden p-2 text-gray-700 hover:text-black ml-[-8px]"
          onClick={toggleSidebar}
        >
          <FaBars size={24} />
        </button>
        <div className="inline-flex items-center">
          <img src={terno} className="logo h-[40px]" alt="Terno logo" />
          <p className="font-semibold">Terno AI</p>
        </div>
    <div className="flex items-center justify-between text-xl p-5 pl-2">
      <div className="flex items-center space-x-3">  
        <button
          className="md:hidden p-2 text-gray-700 hover:text-black ml-[-8px]"
          onClick={toggleSidebar}
        >
          <FaBars size={24} />
        </button>
        <div className="inline-flex items-center">
          <img src={terno} className="logo h-[40px]" alt="Terno logo" />
          <p className="font-semibold">Terno AI</p>
        </div>
      </div>
        <div className="font-semibold">{ds.name}</div>
      
        <ModeToggle />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex flex-row focus-visible:ring-0 font-normal text-base">
            {user.username}
            <ChevronDown />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56 m-5 bg-white">
          <DropdownMenuLabel>
            <div className="font-medium">{user.username}</div>
            <div className="font-light">{user.username}</div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onSelect={(e) => {e.preventDefault()}}
            className="hover:bg-slate-100"
          >
            <div className="w-full">
              <button
                onClick={() => window.open(("/admin"))}
                className="flex w-full gap-2 items-center cursor-pointer"
              >
                <FaArrowUpRightFromSquare />
                <span>Admin</span>
              </button>
            </div>
          </DropdownMenuItem>
          <DropdownMenuItem
            onSelect={(e) => {e.preventDefault()}}
            className="hover:bg-slate-100"
          >
            <div className="w-full">
              <button
                onClick={() => window.open(("/admin"))}
                className="flex w-full gap-2 items-center cursor-pointer"
              >
                <FaArrowUpRightFromSquare />
                <span>Admin</span>
              </button>
            </div>
          </DropdownMenuItem>
          <DropdownMenuItem
            onSelect={(e) => {e.preventDefault()}}
            className="hover:bg-slate-100"
          >
            <div className="w-full">
              <button
                onClick={submit}
                className="flex w-full gap-2 items-center cursor-pointer"
              >
                <LogOut />
                <span>Log out</span>
              </button>
            </div>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default Navbar;