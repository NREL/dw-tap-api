import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './components/Layout';
import About from './components/About';
import Contact from './components/Contact';
import MapView from './components/MapView';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { path: '/', element: <MapView /> },
      { path: '/about', element: <About /> },
      { path: '/contact', element: <Contact /> },
    ]
  }
]
)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)