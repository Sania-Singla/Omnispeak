import express from 'express';
import cors from 'cors';
import CookieParser from 'cookie-parser';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { registerEvents } from './socket.js';

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(CookieParser());

const origins = ['http://localhost:5173', ' http://10.19.186.228:5173']; // for phone dynamic ip address

app.use(
    cors({
        origin: origins,
        credentials: true,
    })
);

app.get('/', (req, res) =>
    res.status(200).json({
        status: 'success',
        message: 'Welcome to Omnispeak!',
    })
);

const http = createServer(app);

export const io = new Server(http, {
    cors: {
        origin: origins,
        credentials: true,
    },
});

io.on('connection', async (socket) => {
    console.log(`User connected: ${socket.id}`);
    registerEvents(io, socket);
});

http.listen(3000, () => {
    console.log('Server is running on port 3000');
});
