import { useState } from "react";
import { getTables } from "../utils/api";
import DropDownMenu from "./DropDownMenu";
import TableColumnAccordian from "./TableColumnAccordian";

const SchemaPane = () => {
  const [tables, setTables] = useState([]);

  const handleSelect = async (value: string) => {
    const response = await getTables(value);
    setTables(response);
  };

  return (
    <div className="mt-8">
      <DropDownMenu onSelect={handleSelect} />
      <div className="mt-4 font-bold text-lg">Allowed Tables</div>
      <TableColumnAccordian data={tables} />
    </div>
  );
};

export default SchemaPane;
