import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu"

const DropDownMenu = () => {
  const [position, setPosition] = useState("bottom");
  return (
    <DropdownMenu>
    <DropdownMenuTrigger asChild>
        <button className='rounded-md border border-slate-400 px-6 py-1'>Open</button>
    </DropdownMenuTrigger>
    <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Choose Data Source</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={position} onValueChange={setPosition}>
        <DropdownMenuRadioItem value="top">First</DropdownMenuRadioItem>
        <DropdownMenuRadioItem value="bottom">Second</DropdownMenuRadioItem>
        <DropdownMenuRadioItem value="right">Third</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
    </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default DropDownMenu