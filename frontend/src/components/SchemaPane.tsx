import { useContext, useState } from "react";
import { getDatasources, getTables } from "../utils/api";
import DataSourceDropDown from "./DataSourceDropDown";
import TableColumnAccordian from "./TableColumnAccordian";
import { UploadIcon } from "lucide-react";
import Uploadfiles from "./Uploadfiles";
import useUserDetails from "../hooks/useUserDetails";
import { DataSourceContext } from "./ui/datasource-context";

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
  const { ds, setDs } = useContext(DataSourceContext);
  const [refreshSignal, setRefreshSignal] = useState(0);

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

  const refreshTables = async (id: string) => {
    const maxRetries = 5;
    let retries = 0;
    let response;
    console.log("Refreshing tables for ID:", id);

    while (retries < maxRetries) {
      response = await getTables(id);
      console.log("Response from getTables:", response);
      if (response.status === "success" && response["table_data"].length > 0) {
        setOriginalTables(response.table_data);
        setFilteredData(response.table_data);
        return;
      }

      retries++;
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    console.warn("❌ Table load failed after upload. Try refreshing manually.");
  };

  const refreshDatasourceDropdown = async (selectId?: string) => {
    const response: { id: string; name: string; suggestions: [] }[] =
      await getDatasources();
    if (response?.length) {
      const defaultId = selectId || response[0].id;
      const selected = response.find((item) => item.id === defaultId);
      setRefreshSignal((prev) => prev + 1);

      if (selected) {
        setDs(selected);
        await handleSelect(defaultId); // triggers table update
      }
    }
  };

  const handleUploadSuccess = async (
    newDsId?: string,
    reloadDsList?: boolean
  ) => {
    if (reloadDsList && newDsId) {
      // Case 1: New DS created → refresh dropdown and tables for new ID
      await refreshDatasourceDropdown(newDsId);
      await refreshTables(newDsId); // only after context has been updated
    } else if (ds?.id) {
      // Case 2: Upload to same datasource
      await refreshTables(ds.id);
    } else {
      console.warn("⚠️ No datasource ID available to refresh tables");
    }
  };

  return (
    <div className="mt-8">
      <div className="flex flex-row justify-center items-center gap-2">
        <DataSourceDropDown
          onSelect={handleSelect}
          refreshSignal={refreshSignal}
        />
        {user.is_admin ? (
          <a
            className="p-2 cursor-pointer rounded-md border border-slate-400"
            onClick={() => setOpen(true)}
          >
            <UploadIcon />
            <Uploadfiles
              open={open}
              setOpen={setOpen}
              dsId={ds.id}
              onUploadSuccess={handleUploadSuccess}
            />
          </a>
        ) : (
          <></>
        )}
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
