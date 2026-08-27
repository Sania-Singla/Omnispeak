import { useState, useRef } from 'react';

// Language ISO codes
const LANGUAGE_OPTIONS = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'pa', name: 'Punjabi' },
];

export function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [isTranslating, setIsTranslating] = useState(false);
    const [inputAudio, setInputAudio] = useState(null);
    const [output, setOutput] = useState(null);
    const [sourceLanguage, setSourceLanguage] = useState('hi');
    const [targetLanguage, setTargetLanguage] = useState('en');

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    async function startRecording() {
        audioChunksRef.current = [];

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
        });

        const recorder = new MediaRecorder(stream);
        mediaRecorderRef.current = recorder;

        recorder.ondataavailable = (event) => {
            audioChunksRef.current.push(event.data);
        };

        recorder.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, {
                type: recorder.mimeType,
            });

            const audioUrl = URL.createObjectURL(audioBlob);

            setInputAudio({ blob: audioBlob, url: audioUrl });

            stream.getTracks().forEach((track) => track.stop());
        };

        recorder.start();
        setIsRecording(true);
    }

    function stopRecording() {
        mediaRecorderRef.current?.stop();
        setIsRecording(false);
    }

    async function translate() {
        setIsTranslating(true);

        try {
            const formData = new FormData();
            formData.append('audio', inputAudio.blob, 'recording.webm');
            formData.append('target_lang', targetLanguage);
            formData.append('source_lang', sourceLanguage);

            const res = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/translate`,
                {
                    method: 'POST',
                    body: formData,
                },
            );

            if (!res.ok) {
                throw new Error('Translation failed');
            }

            const data = await res.json();
            console.log(data);

            setOutput({
                TranscribedText: data.transcription,
                translatedText: data.translation,
                TranslatedAudioUrl: data.audio,
            });
        } catch (err) {
            console.error(err);
        } finally {
            setIsTranslating(false);
        }
    }

    function cancel() {
        setInputAudio(null);
        setOutput(null);
    }

    return (
        <main className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
            <div className="w-full max-w-lg space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    Speech Translator
                </h1>

                {/* Language Dropdowns */}
                <section className="bg-white border rounded-lg p-6 grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            I will speak in:
                        </label>
                        <select
                            value={sourceLanguage}
                            onChange={(e) => setSourceLanguage(e.target.value)}
                            disabled={isRecording || isTranslating}
                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-black focus:border-black disabled:bg-gray-100"
                        >
                            {LANGUAGE_OPTIONS.map((lang) => (
                                <option
                                    key={`src-${lang.code}`}
                                    value={lang.code}
                                >
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Translate to:
                        </label>
                        <select
                            value={targetLanguage}
                            onChange={(e) => setTargetLanguage(e.target.value)}
                            disabled={isTranslating}
                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-black focus:border-black disabled:bg-gray-100"
                        >
                            {LANGUAGE_OPTIONS.map((lang) => (
                                <option
                                    key={`tgt-${lang.code}`}
                                    value={lang.code}
                                >
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </section>

                {/* Recording Operations */}
                <section className="bg-white border rounded-lg p-6 space-y-4">
                    <div className="flex gap-3">
                        <button
                            onClick={startRecording}
                            disabled={isRecording || isTranslating}
                            className="px-4 py-2 bg-black text-white rounded-md disabled:opacity-40"
                        >
                            Record
                        </button>

                        <button
                            onClick={stopRecording}
                            disabled={!isRecording}
                            className="px-4 py-2 border rounded-md disabled:opacity-40"
                        >
                            Stop
                        </button>
                    </div>

                    {isRecording && (
                        <p className="text-sm text-red-500 animate-pulse">
                            Recording...
                        </p>
                    )}
                </section>

                {/* Input Audio Review & Submission */}
                {inputAudio && (
                    <section className="bg-white border rounded-lg p-6 space-y-4">
                        <audio
                            src={inputAudio.url}
                            controls
                            className="w-full"
                        />

                        <div className="flex gap-3">
                            <button
                                onClick={translate}
                                disabled={isTranslating}
                                className="px-4 py-2 bg-black text-white rounded-md disabled:opacity-40"
                            >
                                Translate
                            </button>

                            <button
                                onClick={cancel}
                                disabled={isTranslating}
                                className="px-4 py-2 border rounded-md disabled:opacity-40"
                            >
                                Cancel
                            </button>
                        </div>
                    </section>
                )}

                {/* Loading Status */}
                {isTranslating && (
                    <section className="bg-white border rounded-lg p-6 text-gray-500">
                        Translating...
                    </section>
                )}

                {/* Output Translation Display */}
                {output && (
                    <section className="bg-white border rounded-lg p-6 space-y-4">
                        <h2 className="text-sm font-medium text-gray-500">
                            Translation
                        </h2>
                        <div>
                            <p className="mt-1 text-gray-900">
                                {output.translatedText}
                            </p>

                            <audio
                                src={output.TranslatedAudioUrl}
                                controls
                                className="w-full"
                            />
                        </div>
                    </section>
                )}
            </div>
        </main>
    );
}
