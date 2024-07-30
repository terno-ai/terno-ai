import { useState } from "react";
import { getTables } from "../utils/api";
import DataSourceDropDown from "./DataSourceDropDown";
import TableColumnAccordian from "./TableColumnAccordian";

const SchemaPane = () => {
  const [tables, setTables] = useState([]);

  const handleSelect = async (value: string) => {
    const response = await getTables(value);
    if (response["status"] == "success") {
      setTables(response["table_data"]);
    }
  };

  return (
    <div className="mt-8">
      <DataSourceDropDown onSelect={handleSelect} />
      <div className="mt-4 font-bold text-lg">Allowed Tables</div>
      <TableColumnAccordian data={tables} />
    </div>
  );
};

export default SchemaPane;
