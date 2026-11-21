import { useEffect, useRef, useState } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { useUser } from '../contexts/UserContext';
import { Mic, Dot, Pause, Send, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { LANGUAGES } from '../constants';

const ChatPage = () => {
    const { socket } = useSocket();
    const navigate = useNavigate();
    const { user, setUser } = useUser();
    const [messages, setMessages] = useState([]);
    const [isRecording, setIsRecording] = useState(false);
    const [inputAudio, setInputAudio] = useState(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const [isSending, setIsSending] = useState(false);
    const inputAudioRef = useRef(null);
    const userRef = useRef(user);
    const [memberCount, setMemberCount] = useState(1);

    useEffect(() => {
        if (!socket) return;
        if (!user?.name) {
            navigate('/');
            return;
        }

        socket.on('room-full', () => {
            toast.error('room full');
        });

        socket.on('message-error', (data) => {
            console.log('message-error', data);
            toast.error(data.message);
            setIsSending(false);
        });

        socket.on('room-joined', (data) => {
            toast.success('Room joined successfully!');
            console.log('room-joined', data);
            setMemberCount(data.memberCount);
        });

        socket.on('user-joined', (data) => {
            toast.success(`${data.name} joined the room.`);
            console.log('user-joined', data);
            setMemberCount((prev) => prev + 1);
        });

        socket.on('user-left', (data) => {
            toast.error(`${data.name} left the room.`);
            console.log('user-left', data);
            setMemberCount((prev) => Math.max(prev - 1, 1));
        });

        socket.on('new-message', (data) => {
            const newMessage = {
                name: data.name,
                text: data.text,
                audio_url: data.audio_url,
            };

            console.log('new-message', data);

            setMessages((prev) => [...prev, newMessage]);
        });

        socket.on('message-sent', (data) => {
            const currentAudio = inputAudioRef.current;

            const newMessage = {
                name: userRef.current.name,
                text: data.transcription,
                audio_url: currentAudio?.url,
            };

            setMessages((prev) => [...prev, newMessage]);

            setIsSending(false);

            // Clear audio after successful sending
            setInputAudio(null);
            inputAudioRef.current = null;
        });

        socket.emit('join-room', {
            roomId: 'default',
            name: user.name,
            language: user.language,
        });

        return () => {
            socket.emit('leave-room');
            setUser({ name: '', language: 'en' });

            socket.off('new-message');
            socket.off('message-sent');
            socket.off('room-full');
            socket.off('message-error');
            socket.off('room-joined');
            socket.off('user-joined');
            socket.off('user-left');
        };
    }, [socket, user?.name, navigate]);

    async function startRecording() {
        try {
            audioChunksRef.current = [];

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });

            const recorder = new MediaRecorder(stream);
            mediaRecorderRef.current = recorder;

            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            recorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, {
                    type: recorder.mimeType,
                });

                const audioUrl = URL.createObjectURL(audioBlob);

                const audioData = {
                    blob: audioBlob,
                    url: audioUrl,
                };

                setInputAudio(audioData);
                inputAudioRef.current = audioData;

                stream.getTracks().forEach((track) => track.stop());
            };

            recorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error(err);
            setError(
                'Could not access your microphone. Please allow microphone access.',
            );
        }
    }

    function stopRecording() {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }

        setIsRecording(false);
    }

    async function send() {
        if (!socket || !inputAudio || isSending) return;

        setIsSending(true);

        socket.emit('send-message', {
            audio: inputAudio.blob,
        });
    }

    function cancel() {
        setInputAudio(null);
    }

    return (
        <div className="h-screen bg-slate-950 text-white flex flex-col overflow-hidden">
            {/* Header */}
            <header className="h-16 shrink-0 border-b border-white/10 flex items-center px-5 md:px-8">
                <div className="max-w-4xl w-full mx-auto flex items-center justify-between">
                    <h1 className="text-xl font-bold tracking-tight">
                        Omni<span className="text-indigo-400">Speak</span>
                    </h1>

                    <div className="flex items-center justify-center gap-2">
                        <p className="text-sm font-medium text-blue-600">
                            {LANGUAGES[user.language]}
                        </p>
                        <p>
                            <Dot />
                        </p>
                        <p className="text-sm">
                            {memberCount} participant
                            {memberCount > 1 ? 's' : ''}
                        </p>
                    </div>
                </div>
            </header>

            {/* Chat */}
            <main className="flex-1 min-h-0 w-full max-w-4xl mx-auto flex flex-col px-4 md:px-8">
                {' '}
                <div className="flex-1 min-h-0 overflow-y-auto py-6 space-y-6">
                    {messages.map((message, i) => {
                        const isOwnMessage = message.name === user.name;

                        return (
                            <div
                                key={message.id || i}
                                className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] sm:max-w-[70%] min-w-sm ${
                                        isOwnMessage
                                            ? 'items-end'
                                            : 'items-start'
                                    } flex flex-col`}
                                >
                                    <p
                                        className={`text-xs text-slate-500 mb-1.5 px-1 ${
                                            isOwnMessage
                                                ? 'text-right'
                                                : 'text-left'
                                        }`}
                                    >
                                        {isOwnMessage ? 'You' : message.name}
                                    </p>

                                    <div
                                        className={`rounded-2xl pl-4 pr-[18px] py-3 min-w-sm ${
                                            isOwnMessage
                                                ? 'bg-indigo-600/20 border border-indigo-400/10 rounded-br-sm'
                                                : 'bg-slate-800/80 border border-white/5 rounded-bl-sm'
                                        }`}
                                    >
                                        <p className="text-sm sm:text-base leading-relaxed wrap-break-word">
                                            {message.text}
                                        </p>

                                        {message.audio_url && (
                                            <audio
                                                src={message.audio_url}
                                                controls
                                                className="w-full h-10 mt-3"
                                            />
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {isSending && (
                        <div className="flex justify-end">
                            <div className="bg-indigo-600/10 border border-indigo-400/10 rounded-2xl rounded-br-sm px-4 py-3 flex items-center gap-2 text-sm text-indigo-300">
                                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
                                Translating your message...
                            </div>
                        </div>
                    )}
                </div>
                {/* Bottom Composer */}
                <div className="shrink-0 py-4 border-t border-white/10">
                    <div className="bg-slate-900 border border-white/10 rounded-2xl p-3">
                        {!inputAudio ? (
                            <div className="flex items-center justify-between gap-4">
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-slate-200">
                                        {isRecording
                                            ? 'Recording audio...'
                                            : 'Voice message'}
                                    </p>

                                    <p className="text-xs text-slate-500 mt-1">
                                        {isRecording
                                            ? "Tap stop when you're done"
                                            : 'Tap the microphone to start speaking'}
                                    </p>
                                </div>

                                {!isRecording ? (
                                    <button
                                        type="button"
                                        onClick={startRecording}
                                        className="shrink-0 w-12 cursor-pointer h-12 rounded-full bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center transition"
                                        title="Start recording"
                                    >
                                        <Mic size={21} />
                                    </button>
                                ) : (
                                    <button
                                        type="button"
                                        onClick={stopRecording}
                                        className="shrink-0 w-12 cursor-pointer h-12 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition animate-pulse"
                                        title="Stop recording"
                                    >
                                        <Pause size={21} />
                                    </button>
                                )}
                            </div>
                        ) : (
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-slate-200">
                                        Review your recording
                                    </p>

                                    <span className="text-xs text-slate-500">
                                        Ready to send
                                    </span>
                                </div>

                                <audio
                                    src={inputAudio.url}
                                    controls
                                    className="w-full h-10"
                                />

                                <div className="flex justify-end items-center gap-2">
                                    <button
                                        type="button"
                                        onClick={cancel}
                                        className="px-4 py-2 rounded-xl cursor-pointer text-sm text-slate-400 hover:text-white hover:bg-white/5 transition flex items-center gap-2"
                                    >
                                        <X size={16} />
                                        Discard
                                    </button>

                                    <button
                                        type="button"
                                        onClick={send}
                                        disabled={isSending}
                                        className="px-5 py-2 cursor-pointer rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-sm font-medium flex items-center gap-2 transition"
                                    >
                                        <Send size={15} />
                                        Send
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    <p className="text-center text-[11px] text-slate-600 mt-3">
                        Your voice is automatically translated for other
                        participants.
                    </p>
                </div>
            </main>
        </div>
    );
};

export default ChatPage;
