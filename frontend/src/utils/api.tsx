export const sendMessage = async (prompt: string) => {
    const dummy_query = 'SELECT * FROM invoices';
    return dummy_query
}

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_BASE_URL = '127.0.0.1:8000';

export const endpoints = {
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