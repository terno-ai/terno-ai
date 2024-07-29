import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from "@radix-ui/react-dropdown-menu";
import { FaAngleDown } from "react-icons/fa6";

interface LimitProps {
  limit: string;
  setLimit: (value: string) => void;
}

const LimitSelector: React.FC<LimitProps> = ({limit, setLimit}) => {
  const handleSelect = (limit: string) => {
    setLimit(limit);
  }
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="mt-4 px-4 rounded-md border border-slate-400 flex justify-center items-center hover:bg-slate-100">
          Limit
          <FaAngleDown />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[100px] bg-slate-100">
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={limit} onValueChange={handleSelect}>
          <DropdownMenuRadioItem value="10">10</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="100">100</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="1000">1000</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LimitSelector;
