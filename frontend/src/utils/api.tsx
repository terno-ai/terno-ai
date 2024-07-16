export const getCsrfToken = () => {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  return cookieValue;
};

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_BASE_URL = "";

export const endpoints = {
  getSQL: () => `${API_BASE_URL}/get-sql/`,
  executeSQL: () => `${API_BASE_URL}/execute-sql`,
  getDatasource: () => `${API_BASE_URL}/get-datasource`,
  getTables: (id: string) => `${API_BASE_URL}/get-tables/${id}`,
};

export const sendMessage = async (prompt: string, datasourceId: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getSQL(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify({ prompt: prompt, datasourceId: datasourceId }),
  });
  const result = await response.json();
  return result["generated_sql"];
};

export const executeSQL = async (sql: string, datasourceId: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.executeSQL(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify({ sql: sql, datasourceId: datasourceId }),
  });
  const result = await response.json();
  return result;
};

export const getDatasource = async () => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getDatasource(), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
  });
  const result = await response.json();
  return result["datasources"];
};

export const getTables = async (datasourceId: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getTables(datasourceId), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
  });
  const result = await response.json();
  console.log(result["table_data"]);
  return result["table_data"];
};
