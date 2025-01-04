import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Home from "./pages/HomePage";
import Settings from "./pages/Settings";
import { lazy } from "react";
import Console from "./pages/Console";
const ProviderCallback = lazy(() => import("./pages/ProviderCallback"));
const RequestPasswordReset = lazy(() => import("./pages/RequestPasswordReset"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
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
    path: "console",
    element: <Console />,
  },
  {
    path: "accounts/login",
    element: <Login />,
  },
  {
    path: "accounts/provider/callback",
    element: <ProviderCallback />,
  },
  {
    path: "accounts/password/reset",
    element: <RequestPasswordReset />,
  },
  {
    path: "accounts/password/reset/key/:key",
    element: <ResetPassword />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
