import { useContext, useEffect, useState } from "react";
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
import { getDatasources } from "../utils/api";
import { DataSourceContext } from "./ui/datasource-context";

interface DataSourceDropDownProps {
  onSelect: (value: string, type: string) => void;
}

const DataSourceDropDown: React.FC<DataSourceDropDownProps> = ({
  onSelect,
}) => {
  const [position, setPosition] = useState("");
  const [datasources, setDatasources] = useState<
    { id: string; name: string; type: string }[]
  >([]);
  const { setDs } = useContext(DataSourceContext);

  const handleSelect = (id: string) => {
    setPosition(id);
    const selectedDb = datasources.find((db) => db["id"] === id);
    onSelect(id, selectedDb?.type || "");
    console.log("This is the selected db", selectedDb);
    if (selectedDb) {
      setDs(selectedDb);
    }
  };

  useEffect(() => {
    const fetchDatasources = async () => {
      const response = await getDatasources();
      setDatasources(response);
      console.log(response);
      if (response) {
        onSelect(response[0]["id"], response[0]["type"]);
        setPosition(response[0]["id"]);
        setDs(response[0]);
      }
    };
    fetchDatasources();
  }, []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="w-full rounded-md border border-slate-400 px-6 py-2 flex justify-center items-center hover:bg-slate-100">
          {position ? (
            <span>
              {datasources
                .filter((d) => d["id"] === position)
                .map((ds) => (
                  <span>{ds["name"]}</span>
                ))}
            </span>
          ) : (
            "Data Source"
          )}
          <FaAngleDown />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[300px] bg-white">
        <DropdownMenuLabel className="text-center">
          Choose Data Source
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={position} onValueChange={handleSelect}>
          {datasources.map((row) => (
            <DropdownMenuRadioItem
              value={row["id"]}
              key={row["id"]}
              className="hover:bg-slate-100"
            >
              {row["name"]}
            </DropdownMenuRadioItem>
          ))}
          <DropdownMenuRadioItem
            value="create-new"
            key="create-new"
            className="hover:bg-slate-100 font-bold"
          >
            + Create New Data Source
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default DataSourceDropDown;
