export const sendMessage = async (prompt: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getSQL(), {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      'X-CSRFToken': csrfToken || ''
    },
    body: JSON.stringify({'prompt': prompt})
  });
  const result = await response.json();
  return result['generated_sql'];
}

export const executeSQL = async (sql: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.executeSQL(), {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      'X-CSRFToken': csrfToken || ''
    },
    body: JSON.stringify({'sql': sql})
  });
  const result = await response.json();
  return result['table_data'];
}

export const getDatasource = async () => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getDatasource(), {
    method: 'GET',
    headers: {
      "Content-Type": "application/json",
      'X-CSRFToken': csrfToken || ''
    },
  });
  const result = await response.json();
  return result['datasources'];
}

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_BASE_URL = '';

export const endpoints = {
  getSQL: () => `${API_BASE_URL}/get-sql/`,
  executeSQL: () => `${API_BASE_URL}/execute-sql`,
  getDatasource: () => `${API_BASE_URL}/get-datasource`,
  getUser: (userId: string) => `${API_BASE_URL}/users/${userId}`,
  getPosts: () => `${API_BASE_URL}/posts`,
  createPost: () => `${API_BASE_URL}/posts`,
  updatePost: (postId: string) => `${API_BASE_URL}/posts/${postId}`,
  deletePost: (postId: string) => `${API_BASE_URL}/posts/${postId}`,
};

export const table_data = {
    "columns": ["Invoice", "Status", "Method", "Amount"],
    "data": [
      {
        "id": 1,
        "Invoice": "INV001",
        "Status": "Paid",
        "Method": "Credit Card",
        "Amount": "$250.00",
      },
      {
        "id": 2,
        "Invoice": "INV002",
        "Status": "Pending",
        "Method": "PayPal",
        "Amount": "$150.00",
      }
    ]
}

export const getCsrfToken = () => {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  return cookieValue;
};
