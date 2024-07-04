import { useEffect, useState } from "react";
import { getTables } from "../utils/api";
import DropDownMenu from "./DropDownMenu";

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
      <div className="mt-4 font-bold">Allowed Tables</div>
      <div>
        {tables.map((row, rowIndex) => (
          <div key={rowIndex.toString()} className="">
            {row}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SchemaPane;
