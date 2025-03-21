import React, { createContext, useState, ReactNode } from 'react';

interface DataSource {
  id: string,
  name: string,
  suggestions: string[]
}

interface DataSourceContextProps {
  ds: DataSource;
  setDs: React.Dispatch<React.SetStateAction<DataSource>>;
}
const defaultValue: DataSourceContextProps = {
  ds: { id: '', name: '', suggestions: [] },
  setDs: () => {},
};

export const DataSourceContext = createContext(defaultValue);

export const DataSourceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [ds, setDs] = useState<DataSource>(defaultValue.ds);

  return (
    <DataSourceContext.Provider value={{ds, setDs}}>
      {children}
    </DataSourceContext.Provider>
  );
};
