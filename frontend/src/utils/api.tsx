export const getCsrfToken = () => {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("ternoapp_csrftoken="))
    ?.split("=")[1];

  return cookieValue;
};

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_BASE_URL = "";

export const endpoints = {
  getSQL: () => `${API_BASE_URL}/get-sql/`,
  executeSQL: () => `${API_BASE_URL}/execute-sql`,
  exportSQLResult: () => `${API_BASE_URL}/export-sql-result`,
  getDatasources: () => `${API_BASE_URL}/get-datasources`,
  getTables: (id: string) => `${API_BASE_URL}/get-tables/${id}`,
  getUserDetails: () => `${API_BASE_URL}/get-user-details`,
  getConsoleSQL: () => `${API_BASE_URL}/console/`,
  checkUserExists: () => `${API_BASE_URL}/check-user`,
  fileUpload: () => `${API_BASE_URL}/file-upload`,
  login: () => `${API_BASE_URL}/_allauth/browser/v1/auth/login`,
  requestPasswordReset: () =>
    `${API_BASE_URL}/_allauth/browser/v1/auth/password/request`,
  resetPassword: () =>
    `${API_BASE_URL}/_allauth/browser/v1/auth/password/reset`,
  logout: () => `${API_BASE_URL}/_allauth/browser/v1/auth/session`,
  getDatasourceName: (dsId: string) => `${API_BASE_URL}/datasources/${dsId}/`,
};

export const sendMessage = async (prompt: string, datasourceId: string) => {
  const csrfToken = getCsrfToken();
  try {
    const response = await fetch(endpoints.getSQL(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({ prompt: prompt, datasourceId: datasourceId }),
    });
    if (!response.ok) {
      return {
        status: "error",
        error: `Error: ${response.status} - ${response.statusText}`,
      };
    }
    const result = await response.json();
    return result;
  } catch (error: any) {
    return { status: "error", error: error.message };
  }
};

export const executeSQL = async (
  sql: string,
  datasourceId: string,
  page: number
) => {
  const csrfToken = getCsrfToken();
  try {
    const response = await fetch(endpoints.executeSQL(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({
        sql: sql,
        datasourceId: datasourceId,
        page: page,
      }),
    });
    if (!response.ok) {
      return {
        status: "error",
        error: `Error: ${response.status} - ${response.statusText}`,
      };
    }
    const result = await response.json();
    return result;
  } catch (error: any) {
    return { status: "error", error: error.message };
  }
};

export const exportSQLResult = async (sql: string, datasourceId: string) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.exportSQLResult(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify({ sql: sql, datasourceId: datasourceId }),
  });

  const contentDisposition = response.headers.get("Content-Disposition");
  let fileName = "Query_Results";
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?(.+)"?/);
    if (match && match[1]) {
      fileName = match[1].trim();
    }
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName!;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

export const getDatasources = async () => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getDatasources(), {
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
  return result;
};

export const getUserDetails = async () => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getUserDetails(), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
  });
  const result = await response.json();
  return result;
};

export const sendConsoleMessage = async (
  datasourceId: string,
  systemPrompt: string,
  assistantMessage: string,
  userPrompt: string
) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.getConsoleSQL(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify({
      datasourceId: datasourceId,
      systemPrompt: systemPrompt,
      assistantMessage: assistantMessage,
      userPrompt: userPrompt,
    }),
  });
  const result = await response.json();
  return result;
};

export const checkUserExists = async (data: any) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.checkUserExists(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  return result;
};

export const login = async (data: any) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.login(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  return result;
};

export const requestPasswordReset = async (data: any) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.requestPasswordReset(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  return result;
};

export const resetPassword = async (data: any) => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.resetPassword(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  return result;
};

export const logout = async () => {
  const csrfToken = getCsrfToken();
  const response = await fetch(endpoints.logout(), {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
    },
  });
  const result = await response.json();
  return result;
};

export const fileUpload = async (formData: FormData) => {
  const csrfToken = getCsrfToken();

  const response = await fetch(endpoints.fileUpload(), {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken || "",
    },
    body: formData,
  });
  const result = await response.json();
  return result;
};

export const getDatasourceName = async (dsId: string) => {
  const csrfToken = getCsrfToken();

  const response = await fetch(endpoints.getDatasourceName(dsId), {
    method: "GET",
    headers: {
      "X-CSRFToken": csrfToken || "",
      "Content-Type": "application/json",
    },
  });

  const result = await response.json();
  console.log(result);
  return result;
};

// WebSocket message types
export type WebSocketMessageType = 'chat' | 'notification';

interface WebSocketMessage {
  type: WebSocketMessageType;
  message: string;
  data?: any;
}

export class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private messageHandlers: Map<WebSocketMessageType, ((data: any) => void)[]> = new Map();

  private constructor() {
    this.messageHandlers.set('chat', []);
    this.messageHandlers.set('notification', []);
  }

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  public connect() {
    if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
      this.ws = new WebSocket(`ws://127.0.0.1:8000/ws/agent/`);
      
      this.ws.onmessage = (event) => {
        const data: WebSocketMessage = JSON.parse(event.data);
        const handlers = this.messageHandlers.get(data.type) || [];
        handlers.forEach(handler => handler(data));
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyHandlers('notification', { status: 'error', message: 'Connection failed' });
      };

      this.ws.onclose = () => {
        console.log('WebSocket connection closed');
        setTimeout(() => this.connect(), 5000);
      };
    }
  }

  public subscribe(type: WebSocketMessageType, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(type) || [];
    handlers.push(handler);
    this.messageHandlers.set(type, handlers);
  }

  public unsubscribe(type: WebSocketMessageType, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(type) || [];
    const index = handlers.indexOf(handler);
    if (index !== -1) {
      handlers.splice(index, 1);
      this.messageHandlers.set(type, handlers);
    }
  }

  public send(type: WebSocketMessageType, message: string, data?: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, message, data }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  private notifyHandlers(type: WebSocketMessageType, data: any) {
    const handlers = this.messageHandlers.get(type) || [];
    handlers.forEach(handler => handler(data));
  }
}

export const sendChatMessage = (message: string) => {
  const ws = WebSocketService.getInstance();
  ws.send('chat', message);
};

export const subscribeToChat = (handler: (data: any) => void) => {
  const ws = WebSocketService.getInstance();
  ws.subscribe('chat', handler);
  return () => ws.unsubscribe('chat', handler);
};

export const subscribeToNotifications = (handler: (data: any) => void) => {
  const ws = WebSocketService.getInstance();
  ws.subscribe('notification', handler);
  return () => ws.unsubscribe('notification', handler);
};
