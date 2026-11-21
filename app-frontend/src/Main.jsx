import { createRoot } from 'react-dom/client';
import './index.css';
import { RouterProvider } from 'react-router-dom';
import { router } from './Router.jsx';
import { SocketProvider } from './contexts/SocketContext.jsx';
import { UserProvider } from './contexts/UserContext.jsx';
import { Toaster } from 'react-hot-toast';

createRoot(document.getElementById('root')).render(
    <UserProvider>
        <SocketProvider>
            <RouterProvider router={router} />
            <Toaster position="top-right" />
        </SocketProvider>
    </UserProvider>,
);
