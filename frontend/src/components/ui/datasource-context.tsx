import React, { createContext, useState, ReactNode } from "react";

interface DataSource {
  id: string;
  name: string;
  type: string;
}

interface DataSourceContextProps {
  ds: DataSource;
  setDs: React.Dispatch<React.SetStateAction<DataSource>>;
}
const defaultValue: DataSourceContextProps = {
  ds: { id: "", name: "", type: "" },
  setDs: () => {},
};

export const DataSourceContext = createContext(defaultValue);

export const DataSourceProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [ds, setDs] = useState({ id: "", name: "", type: "" });

  return (
    <DataSourceContext.Provider value={{ ds, setDs }}>
      {children}
    </DataSourceContext.Provider>
  );
};
