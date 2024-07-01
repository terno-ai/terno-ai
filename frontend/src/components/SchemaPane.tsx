import { useEffect, useState } from "react";
import { getTables } from "../utils/api";
import DropDownMenu from "./DropDownMenu";

const SchemaPane = () => {
  const [tables, setTables] = useState([]);

  useEffect(() => {
    const fetchDatasource = async () => {
      const response = await getTables();
      setTables(response);
    };
    fetchDatasource();
  }, []);

  return (
    <div>
        <DropDownMenu />
        <div className="font-bold">Allowed Tables</div>
        <div>
        {tables.map((row, rowIndex) => (
            <div
                key={rowIndex.toString()}
                className=""
            >
                {row}
            </div>
        ))}
        </div>
    </div>
  )
}

export default SchemaPane