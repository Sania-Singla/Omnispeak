import { SOCKET_EVENTS } from './constants.js';

const users = new Map();

const MAX_USERS_PER_ROOM = 5;
const PYTHON_API = 'http://localhost:8000/api/v1/audio-translate-many';

export function registerEvents(io, socket) {
    // JOIN ROOM
    socket.on(
        SOCKET_EVENTS.JOIN_ROOM,
        async ({ roomId, name, language } = {}) => {
            try {
                if (!roomId || !name || !language) return;

                const prevUser = users.get(socket.id);

                // Check room capacity before removing old membership
                const roomSize =
                    io.sockets.adapter.rooms.get(roomId)?.size || 0;

                const alreadyInSameRoom = prevUser?.roomId === roomId;

                if (!alreadyInSameRoom && roomSize >= MAX_USERS_PER_ROOM) {
                    socket.emit(SOCKET_EVENTS.ROOM_FULL);
                    return;
                }

                // Leave previous room if necessary
                if (prevUser) {
                    await socket.leave(prevUser.roomId);

                    socket.to(prevUser.roomId).emit('user-left', {
                        name: prevUser.name,
                    });

                    users.delete(socket.id);
                }

                // Add user to Map
                users.set(socket.id, {
                    name,
                    roomId,
                    language,
                });

                // Join new room
                await socket.join(roomId);

                // Confirm to the newly joined user
                socket.emit(SOCKET_EVENTS.ROOM_JOINED, {
                    name,
                    language,
                    memberCount:
                        io.sockets.adapter.rooms.get(roomId)?.size || 1,
                });

                // Notify all existing users in the room
                socket.to(roomId).emit(SOCKET_EVENTS.USER_JOINED, {
                    name,
                    language,
                });

                console.log(`${name} joined room ${roomId}`);
                console.log(users);
            } catch (error) {
                console.error('Join room error:', error);
            }
        }
    );

    // LEAVE ROOM
    socket.on(SOCKET_EVENTS.LEAVE_ROOM, async () => {
        const user = users.get(socket.id);

        if (!user) return;

        await socket.leave(user.roomId);

        console.log(`${user.name} left room ${user.roomId}`);

        users.delete(socket.id);

        socket
            .to(user.roomId)
            .emit(SOCKET_EVENTS.USER_LEFT, { name: user.name });

        console.log(users);
    });

    // SEND MESSAGE
    socket.on(
        SOCKET_EVENTS.SEND_MESSAGE,
        async ({ audio, model_name = 'nllb' } = {}) => {
            const sender = users.get(socket.id);

            if (!audio) {
                return;
            }

            try {
                // 1. Get socket IDs
                const roomSocketIds =
                    io.sockets.adapter.rooms.get(sender.roomId) || new Set();

                // 2. Exclude sender and retrieve receiver information.
                const receivers = [...roomSocketIds]
                    .filter((socketId) => socketId !== socket.id)
                    .map((socketId) => {
                        const user = users.get(socketId);

                        if (!user) return null;

                        return {
                            socketId,
                            name: user.name,
                            language: user.language,
                        };
                    })
                    .filter(Boolean);

                // 3. Get unique target languages.
                const targetLanguages = [
                    ...new Set(receivers.map((receiver) => receiver.language)),
                ];

                // 4. Convert received audio into Buffer.
                let audioBuffer;

                if (Buffer.isBuffer(audio)) {
                    audioBuffer = audio;
                } else if (audio instanceof ArrayBuffer) {
                    audioBuffer = Buffer.from(audio);
                } else if (ArrayBuffer.isView(audio)) {
                    audioBuffer = Buffer.from(
                        audio.buffer,
                        audio.byteOffset,
                        audio.byteLength
                    );
                } else {
                    throw new Error('Invalid audio format.');
                }

                // 5. Create audio Blob.
                const audioBlob = new Blob([audioBuffer], {
                    type: 'audio/webm',
                });

                // 6. Prepare FormData for Python API.
                const formData = new FormData();

                formData.append('audio', audioBlob, 'recording.webm');
                formData.append('source_lang', sender.language);
                formData.append('model_name', model_name);

                targetLanguages.forEach((language) => {
                    formData.append('target_langs', language);
                });

                // 7. Call Python API (STT once + translation/TTS for each unique language)
                const res = await fetch(PYTHON_API, {
                    method: 'POST',
                    body: formData,
                });

                if (!res.ok) {
                    const errorData = await res.json().catch(() => null);
                    throw new Error(errorData?.detail || 'Translation failed.');
                }

                const data = await res.json();

                console.log('python api response:', data);

                // 8. Validate translations BEFORE sending success to sender.

                const missingLanguages = targetLanguages.filter(
                    (language) =>
                        !data.results?.some(
                            (item) => item.language === language
                        )
                );

                if (missingLanguages.length > 0) {
                    // Notify receivers whose translations are unavailable.
                    for (const receiver of receivers) {
                        if (missingLanguages.includes(receiver.language)) {
                            io.to(receiver.socketId).emit(
                                SOCKET_EVENTS.MESSAGE_ERROR,
                                {
                                    message: `Translation unavailable for ${receiver.language}.`,
                                }
                            );
                        }
                    }

                    // Notify sender also.
                    socket.emit(SOCKET_EVENTS.MESSAGE_ERROR, {
                        message:
                            'Message could not be delivered to all receivers.',
                    });

                    return;
                }

                // 9. All translations are available. Now deliver messages.

                for (const receiver of receivers) {
                    if (!io.sockets.sockets.has(receiver.socketId)) {
                        continue;
                    }

                    const result = data.results.find(
                        (item) => item.language === receiver.language
                    );

                    io.to(receiver.socketId).emit(SOCKET_EVENTS.NEW_MESSAGE, {
                        name: sender.name,
                        language: sender.language,
                        targetLanguage: receiver.language,
                        text: result.translation,
                        audio_url: result.audio_url,
                    });
                }

                // 10. Notify sender ONLY after successful delivery processing.

                socket.emit(SOCKET_EVENTS.MESSAGE_SENT, {
                    name: sender.name,
                    language: sender.language,
                    transcription: data.transcription,
                });
            } catch (error) {
                socket.emit(SOCKET_EVENTS.MESSAGE_ERROR, {
                    message:
                        error.message ||
                        'An error occurred while sending the message.',
                });
                console.error('Send message error:', error);
            }
        }
    );

    // DISCONNECT
    socket.on(SOCKET_EVENTS.DISCONNECT, () => {
        const user = users.get(socket.id);

        if (user) {
            console.log(`${user.name} disconnected from room ${user.roomId}`);
            users.delete(socket.id);
        }
    });
}

export { users };
