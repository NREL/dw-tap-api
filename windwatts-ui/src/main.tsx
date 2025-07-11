import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./components/Layout";
import MapView from "./components/MapView";
import SettingsProvider from "./providers/SettingsProvider";
import UnitsProvider from "./providers/UnitsProvider";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [{ path: "/", element: <MapView /> }],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <SettingsProvider>
      <UnitsProvider>
        <RouterProvider router={router} />
      </UnitsProvider>
    </SettingsProvider>
  </StrictMode>,
);
