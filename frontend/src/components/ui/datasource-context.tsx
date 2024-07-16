import React, { createContext, useState, ReactNode } from 'react';

interface DataSource {
  id: string,
  name: string
}

interface DataSourceContextProps {
  ds: DataSource;
  setDs: React.Dispatch<React.SetStateAction<DataSource>>;
}
const defaultValue: DataSourceContextProps = {
  ds: { id: '', name: '' },
  setDs: () => {},
};

export const DataSourceContext = createContext(defaultValue);

export const DataSourceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [ds, setDs] = useState({ id: '', name: '' });

  return (
    <DataSourceContext.Provider value={{ds, setDs}}>
      {children}
    </DataSourceContext.Provider>
  );
};
