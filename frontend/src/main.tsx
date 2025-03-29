import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Home from "./pages/HomePage";
import Settings from "./pages/Settings";
import Console from "./pages/Console";
import { lazy, Suspense } from "react";
import ChatPage from "./pages/ChatPage";
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
    path: "chat",
    element: <ChatPage />,
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
    element: (
      <Suspense fallback={<div>Loading</div>}>
        <Login />
      </Suspense>
    ),
  },
  {
    path: "accounts/provider/callback",
    element: (
      <Suspense fallback={<div>Loading</div>}>
        <ProviderCallback />
      </Suspense>
    ),
  },
  {
    path: "accounts/password/reset",
    element: (
      <Suspense fallback={<div>Loading</div>}>
        <RequestPasswordReset />
      </Suspense>
    ),
  },
  {
    path: "accounts/password/reset/key/:key",
    element: (
      <Suspense fallback={<div>Loading</div>}>
        <ResetPassword />
      </Suspense>
    ),
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
