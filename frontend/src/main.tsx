import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Home from "./pages/HomePage";
import Settings from "./pages/Settings";
import { lazy } from "react";
import Console from "./pages/Console";
const Login = lazy(() => import("./pages/Login"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "settings",
    element: <Settings />,
  },
  {
    path: "accounts/login",
    element: <Login />,
  },
  {
    path: "console",
    element: <Console />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
