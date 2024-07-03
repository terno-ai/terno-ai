import { useEffect, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { FaAngleDown } from "react-icons/fa";
import { getDatasource } from "../utils/api";

const DropDownMenu = () => {
  const [position, setPosition] = useState("bottom");
  const [datasource, setDatasource] = useState([]);

  useEffect(() => {
    const fetchDatasource = async () => {
      const response = await getDatasource();
      setDatasource(response);
    };
    fetchDatasource();
  }, []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="w-full rounded-md border border-slate-400 px-6 py-1 flex justify-center items-center">
          Data Source
          <FaAngleDown />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[300px] bg-white">
        <DropdownMenuLabel>Choose Data Source</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={position} onValueChange={setPosition}>
          {datasource.map((row, rowIndex) => (
            <DropdownMenuRadioItem
              value={rowIndex.toString()}
              key={rowIndex.toString()}
            >
              {row}
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default DropDownMenu;
