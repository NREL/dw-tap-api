import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./components/Layout";
import About from "./components/About";
import Contact from "./components/Contact";
import MapView from "./components/MapView";
import UnitsProvider from "./providers/UnitsContext";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { path: "/", element: <MapView /> },
      { path: "/about", element: <About /> },
      { path: "/contact", element: <Contact /> },
    ],
  },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <UnitsProvider defaultValues={{ windspeed: "m/s", output: "kWh" }}>
      <RouterProvider router={router} />
    </UnitsProvider>
  </StrictMode>
);
