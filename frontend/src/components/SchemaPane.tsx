import { useEffect, useState } from "react";
import { getTables } from "../utils/api";
import DropDownMenu from "./DropDownMenu";
import TableColumnAccordian from "./TableColumnAccordian";

const SchemaPane = () => {
  const [tables, setTables] = useState([]);

  useEffect(() => {
    const fetchDatasource = async () => {
      const response = await getTables('1');
      setTables(response);
    };
    fetchDatasource();
  }, []);

  return (
    <div className="mt-8">
      <DropDownMenu />
      <div className="mt-4 font-bold text-lg">Allowed Tables</div>
      <TableColumnAccordian data={tables} />
    </div>
  );
};

export default SchemaPane;
