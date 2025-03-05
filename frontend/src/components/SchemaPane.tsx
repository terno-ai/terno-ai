import { useState } from "react";
import { getTables } from "../utils/api";
import DataSourceDropDown from "./DataSourceDropDown";
import TableColumnAccordian from "./TableColumnAccordian";
import { UploadIcon } from "lucide-react";
import Uploadfiles from "./Uploadfiles";
import useUserDetails from "../hooks/useUserDetails";

interface ColumnData {
  public_name: string;
  data_type: string;
}

interface TableData {
  table_name: string;
  table_description: string;
  column_data: ColumnData[];
}

const SchemaPane = () => {
  const [originalTables, setOriginalTables] = useState<TableData[]>([]);
  const [query, setQuery] = useState("");
  const [filteredData, setFilteredData] = useState<TableData[]>([]);
  const [open, setOpen] = useState(false);
  const [user] = useUserDetails();

  const handleSelect = async (value: string) => {
    const response = await getTables(value);
    if (response["status"] == "success") {
      setOriginalTables(response["table_data"]);
      setFilteredData(response["table_data"]);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const searchQuery = event.target.value.toLowerCase();
    setQuery(searchQuery);
    const filteredTables = originalTables.filter((table: TableData) =>
      table.table_name.toLowerCase().includes(searchQuery)
    );
    setFilteredData(filteredTables);
  };

  return (
    <div className="mt-8">
      <div className="flex flex-row justify-center items-center gap-2">
        <DataSourceDropDown onSelect={handleSelect} />
        {user.is_admin ? (
          <a
          className="p-2 cursor-pointer rounded-md border border-slate-400"
          onClick={() => setOpen(true)}
        >
          <UploadIcon />
          <Uploadfiles
            open={open}
            setOpen={setOpen}
          />
        </a>
        ): <></>}
      </div>
      <div className="mt-4 font-bold text-lg">Allowed Tables</div>
      <input
        type="text"
        className="w-full rounded-md border border-slate-400 px-4 py-2 flex justify-center items-center"
        placeholder="Search..."
        value={query}
        onChange={handleSearch}
      />
      <TableColumnAccordian data={filteredData} />
    </div>
  );
};

export default SchemaPane;
