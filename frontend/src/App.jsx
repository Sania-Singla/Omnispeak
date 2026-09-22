import { useEffect, useRef, useState } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const LANGUAGE_OPTIONS = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'pa', name: 'Punjabi' },
];

const MODEL_NAMES = {
    nllb: 'NLLB-200',
    m2m100: 'M2M100',
    mbart: 'mBART-50',
    marian: 'MarianMT',
    gemini: 'Gemini',
    indictrans2: 'IndicTrans2',
};

// Har model ka demonstration role evaluator ko explain karne ke liye
const MODEL_BADGES = {
    gemini: {
        label: 'Top Cloud Accuracy',
        color: 'bg-purple-100 text-purple-800',
    },
    nllb: {
        label: 'Offline Production Standard',
        color: 'bg-emerald-100 text-emerald-800',
    },
    mbart: {
        label: 'Bilingual High-Accuracy (67.6 BLEU)',
        color: 'bg-blue-100 text-blue-800',
    },
    marian: {
        label: 'Ultra-Fast / Low Footprint (~300MB)',
        color: 'bg-cyan-100 text-cyan-800',
    },
    m2m100: {
        label: 'Tokenization Sensitive (Legacy)',
        color: 'bg-amber-100 text-amber-800',
    },
};

// Har language pair ke benchmark insights demonstration ke liye
const PAIR_INSIGHTS = {
    'hi-en': {
        best: 'Gemini (83.73 BLEU)',
        notable:
            'mBART (67.65) matches NLLB (68.34); MarianMT offers fast CPU inference (52.11).',
        evalNote: 'Compare mBART vs NLLB vs Gemini on English fluency.',
    },
    'en-hi': {
        best: 'Gemini (69.02 BLEU)',
        notable:
            'NLLB leads offline (62.48); mBART scores 46.94; MarianMT drops to 22.26.',
        evalNote:
            'Demonstrates Devanagari verb agreement handling across architectures.',
    },
    'pa-hi': {
        best: 'Gemini (86.97 BLEU)',
        notable:
            'Indo-Aryan cognate alignment; NLLB achieves 70.55 BLEU, M2M-100 drops to 18.94.',
        evalNote:
            'Shows strong transfer between syntactically close Indic languages.',
    },
    'hi-pa': {
        best: 'Gemini (78.83 BLEU)',
        notable:
            'NLLB is the only viable local model (37.94); M2M-100 collapses (0.39 BLEU).',
        evalNote: 'Gurmukhi tokenization bottleneck demonstration case study.',
    },
    'pa-en': {
        best: 'Gemini (83.33 BLEU)',
        notable:
            'NLLB scores 63.88; MarianMT reaches 35.28; M2M-100 drops to 16.82.',
        evalNote:
            'Highlights vocabulary coverage differences across subword tokenizers.',
    },
    'en-pa': {
        best: 'Gemini (62.15 BLEU)',
        notable:
            'NLLB retains 53.09 BLEU; M2M-100 fails at 0.37 BLEU and 132.39 TER.',
        evalNote:
            'Clear demonstration of subword vocabulary failure on Gurmukhi script.',
    },
};

export function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [isTranslating, setIsTranslating] = useState(false);
    const [inputAudio, setInputAudio] = useState(null);
    const [output, setOutput] = useState(null);
    const [error, setError] = useState(null);
    const [sourceLanguage, setSourceLanguage] = useState('hi');
    const [targetLanguage, setTargetLanguage] = useState('en');
    const [availableModels, setAvailableModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState('nllb');
    const [isLoadingModels, setIsLoadingModels] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const pairKey = `${sourceLanguage}-${targetLanguage}`;
    const pairInsight = PAIR_INSIGHTS[pairKey];

    // Language pair change hone par supported models load karna
    useEffect(() => {
        async function fetchAvailableModels() {
            setIsLoadingModels(true);
            setError(null);

            try {
                const params = new URLSearchParams({
                    source_lang: sourceLanguage,
                    target_lang: targetLanguage,
                });

                const response = await fetch(
                    `${BACKEND_URL}/translation-models?${params.toString()}`,
                );

                if (!response.ok) {
                    throw new Error(
                        'Could not load available translation models.',
                    );
                }

                const models = await response.json();
                setAvailableModels(models);

                // Default priority: Agar NLLB available hai toh local safe choice choose karein
                if (models.includes(selectedModel)) {
                    // Selection maintain rahegi
                } else if (models.includes('nllb')) {
                    setSelectedModel('nllb');
                } else if (models.length > 0) {
                    setSelectedModel(models[0]);
                } else {
                    setSelectedModel('');
                }
            } catch (err) {
                console.error(err);
                setAvailableModels([]);
                setSelectedModel('');
                setError('Could not load models for this language pair.');
            } finally {
                setIsLoadingModels(false);
            }
        }

        fetchAvailableModels();
    }, [sourceLanguage, targetLanguage]);

    async function startRecording() {
        setError(null);
        setOutput(null);

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

                setInputAudio({
                    blob: audioBlob,
                    url: audioUrl,
                });

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

    async function translate() {
        if (!inputAudio) {
            setError('Please record something first.');
            return;
        }

        if (!selectedModel) {
            setError(
                'No translation model is available for this language pair.',
            );
            return;
        }

        setIsTranslating(true);
        setError(null);
        setOutput(null);

        try {
            const formData = new FormData();
            formData.append('audio', inputAudio.blob, 'recording.webm');
            formData.append('source_lang', sourceLanguage);
            formData.append('target_lang', targetLanguage);
            formData.append('provider', selectedModel);

            const response = await fetch(`${BACKEND_URL}/translate`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || 'Translation failed.');
            }

            const data = await response.json();

            setOutput({
                transcription: data.transcription,
                translation: data.translation,
                audio: data.audio,
                scores: data.scores || null,
                provider: data.provider || selectedModel,
            });
        } catch (err) {
            console.error(err);
            setError(err.message || 'Translation failed.');
        } finally {
            setIsTranslating(false);
        }
    }

    function cancel() {
        if (inputAudio?.url) {
            URL.revokeObjectURL(inputAudio.url);
        }
        setInputAudio(null);
        setOutput(null);
        setError(null);
    }

    function swapLanguages() {
        setSourceLanguage(targetLanguage);
        setTargetLanguage(sourceLanguage);
        setOutput(null);
    }

    return (
        <main className="min-h-screen bg-gray-50 p-6 font-sans">
            <div className="w-full max-w-2xl mx-auto space-y-6">
                {/* Header */}
                <header className="pt-4">
                    <h1 className="text-3xl font-bold text-gray-900">
                        OmniSpeak
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Modular Speech-to-Speech Translation across Indian
                        Languages
                    </p>
                </header>

                {/* Translation Settings & Benchmark Demonstration Section */}
                <section className="bg-white border border-gray-200 rounded-xl p-6 space-y-5 shadow-xs">
                    <div>
                        <h2 className="text-base font-semibold text-gray-900">
                            Translation Settings & Model Benchmark
                        </h2>
                        <p className="text-sm text-gray-500 mt-1">
                            Select source/target languages and compare different
                            translation architectures.
                        </p>
                    </div>

                    {/* Language Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                I will speak in
                            </label>
                            <select
                                value={sourceLanguage}
                                onChange={(e) =>
                                    setSourceLanguage(e.target.value)
                                }
                                disabled={isRecording || isTranslating}
                                className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black disabled:bg-gray-100"
                            >
                                {LANGUAGE_OPTIONS.map((lang) => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Swap Button */}
                        <button
                            type="button"
                            onClick={swapLanguages}
                            disabled={isRecording || isTranslating}
                            className="px-3.5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 font-semibold"
                            title="Swap languages"
                        >
                            ⇄
                        </button>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Translate to
                            </label>
                            <select
                                value={targetLanguage}
                                onChange={(e) =>
                                    setTargetLanguage(e.target.value)
                                }
                                disabled={isRecording || isTranslating}
                                className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black disabled:bg-gray-100"
                            >
                                {LANGUAGE_OPTIONS.map((lang) => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Evaluator Pair Benchmark Insight Card */}
                    {pairInsight && (
                        <div className="bg-slate-50 border border-slate-200/90 rounded-lg p-3.5 space-y-1.5 text-xs">
                            <div className="flex items-center justify-between">
                                <span className="font-semibold text-slate-800 uppercase tracking-wide">
                                    Pair Insight: {sourceLanguage.toUpperCase()}{' '}
                                    → {targetLanguage.toUpperCase()}
                                </span>
                                <span className="text-[11px] text-slate-500 font-medium">
                                    Top Benchmark: {pairInsight.best}
                                </span>
                            </div>
                            <p className="text-slate-600 leading-relaxed">
                                {pairInsight.notable}
                            </p>
                            <div className="text-[11px] text-indigo-700 font-medium pt-0.5">
                                Reasoning: {pairInsight.evalNote}
                            </div>
                        </div>
                    )}

                    {/* Model Dropdown with Specific Role Badges */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium text-gray-700">
                                Translation Engine
                            </label>
                            {selectedModel && MODEL_BADGES[selectedModel] && (
                                <span
                                    className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${MODEL_BADGES[selectedModel].color}`}
                                >
                                    {MODEL_BADGES[selectedModel].label}
                                </span>
                            )}
                        </div>

                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            disabled={
                                isRecording ||
                                isTranslating ||
                                isLoadingModels ||
                                availableModels.length === 0
                            }
                            className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black disabled:bg-gray-100"
                        >
                            {isLoadingModels ? (
                                <option value="">Loading models...</option>
                            ) : availableModels.length === 0 ? (
                                <option value="">No models available</option>
                            ) : (
                                availableModels.map((model) => {
                                    const badge = MODEL_BADGES[model]?.label;
                                    return (
                                        <option key={model} value={model}>
                                            {MODEL_NAMES[model] || model}{' '}
                                            {badge ? `— [${badge}]` : ''}
                                        </option>
                                    );
                                })
                            )}
                        </select>

                        {/* Quick Selection Pills for Fast Evaluator Switching */}
                        {!isLoadingModels && availableModels.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-1.5 items-center">
                                <span className="text-[11px] text-gray-400 mr-1 font-medium">
                                    Quick Select:
                                </span>
                                {availableModels.map((model) => (
                                    <button
                                        key={model}
                                        type="button"
                                        onClick={() => setSelectedModel(model)}
                                        className={`text-[11px] px-2.5 py-1 rounded-md border transition-all ${
                                            selectedModel === model
                                                ? 'bg-black text-white border-black font-semibold shadow-xs'
                                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                        }`}
                                    >
                                        {MODEL_NAMES[model] || model}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </section>

                {/* Error Banner */}
                {error && (
                    <section className="bg-red-50 border border-red-200 rounded-xl p-4">
                        <p className="text-sm text-red-700">{error}</p>
                    </section>
                )}

                {/* Audio Recording Section */}
                <section className="bg-white border border-gray-200 rounded-xl p-6 space-y-5 shadow-xs">
                    <div>
                        <h2 className="text-base font-semibold text-gray-900">
                            Record Speech
                        </h2>
                        <p className="text-sm text-gray-500 mt-1">
                            Record spoken input through microphone for
                            sequential STT → NMT → TTS execution.
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-3">
                        <button
                            type="button"
                            onClick={startRecording}
                            disabled={isRecording || isTranslating}
                            className="px-5 py-2.5 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-40"
                        >
                            Record
                        </button>

                        <button
                            type="button"
                            onClick={stopRecording}
                            disabled={!isRecording}
                            className="px-5 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-40"
                        >
                            Stop
                        </button>
                    </div>

                    {isRecording && (
                        <div className="flex items-center gap-2 text-sm text-red-600 font-medium">
                            <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
                            Recording in progress...
                        </div>
                    )}
                </section>

                {/* Review Input Audio */}
                {inputAudio && (
                    <section className="bg-white border border-gray-200 rounded-xl p-6 space-y-5 shadow-xs">
                        <div>
                            <h2 className="text-base font-semibold text-gray-900">
                                Your Spoken Input
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">
                                Listen to recorded input before sending it to
                                the pipeline.
                            </p>
                        </div>

                        <audio
                            src={inputAudio.url}
                            controls
                            className="w-full"
                        />

                        <div className="flex flex-wrap gap-3">
                            <button
                                type="button"
                                onClick={translate}
                                disabled={isTranslating || !selectedModel}
                                className="px-5 py-2.5 bg-black text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-40"
                            >
                                {isTranslating
                                    ? 'Translating Pipeline Active...'
                                    : `Translate with ${MODEL_NAMES[selectedModel] || selectedModel}`}
                            </button>

                            <button
                                type="button"
                                onClick={cancel}
                                disabled={isTranslating}
                                className="px-5 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-40"
                            >
                                Cancel
                            </button>
                        </div>
                    </section>
                )}

                {/* Progress Spinner */}
                {isTranslating && (
                    <section className="bg-white border border-gray-200 rounded-xl p-6 shadow-xs">
                        <div className="flex items-center gap-3">
                            <div className="w-5 h-5 border-2 border-gray-300 border-t-black rounded-full animate-spin" />
                            <div>
                                <p className="text-sm font-medium text-gray-900">
                                    Processing Audio Pipeline...
                                </p>
                                <p className="text-xs text-gray-500 mt-0.5">
                                    Running STT →{' '}
                                    {MODEL_NAMES[selectedModel] ||
                                        selectedModel}{' '}
                                    → TTS synthesis
                                </p>
                            </div>
                        </div>
                    </section>
                )}

                {/* Translation & Metrics Result Display */}
                {output && (
                    <section className="bg-white border border-gray-200 rounded-xl p-6 space-y-6 shadow-xs">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-lg font-semibold text-gray-900">
                                    Translation Pipeline Result
                                </h2>
                                <p className="text-sm text-gray-500 mt-1">
                                    {
                                        LANGUAGE_OPTIONS.find(
                                            (l) => l.code === sourceLanguage,
                                        )?.name
                                    }{' '}
                                    →{' '}
                                    {
                                        LANGUAGE_OPTIONS.find(
                                            (l) => l.code === targetLanguage,
                                        )?.name
                                    }
                                </p>
                            </div>

                            <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-semibold text-gray-700">
                                Engine:{' '}
                                {MODEL_NAMES[output.provider] ||
                                    output.provider}
                            </span>
                        </div>

                        {/* Speech-to-Text Transcription */}
                        <div>
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                                1. STT Transcription (Source Speech)
                            </p>
                            <div className="mt-2 bg-gray-50 border border-gray-200 rounded-lg p-4">
                                <p className="text-gray-800 leading-relaxed">
                                    {output.transcription}
                                </p>
                            </div>
                        </div>

                        {/* Machine Translation Output */}
                        <div>
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                                2. Machine Translation Output
                            </p>
                            <div className="mt-2 bg-gray-50 border border-gray-200 rounded-lg p-4">
                                <p className="text-lg font-medium text-gray-900 leading-relaxed">
                                    {output.translation}
                                </p>
                            </div>
                        </div>

                        {/* Synthesized Spoken Audio */}
                        {output.audio && (
                            <div>
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                    3. Synthesized Target Speech (TTS)
                                </p>
                                <audio
                                    src={output.audio}
                                    controls
                                    className="w-full"
                                />
                            </div>
                        )}

                        {/* Evaluation Metrics Block */}
                        {output.scores && (
                            <div className="pt-3 border-t border-gray-100">
                                <div className="flex items-center justify-between mb-3">
                                    <p className="text-xs font-bold text-gray-600 uppercase tracking-wide">
                                        Evaluation Benchmark Metrics
                                    </p>
                                    <span className="text-[11px] text-gray-400">
                                        Automated reference validation
                                    </span>
                                </div>

                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                    {/* BLEU */}
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                                        <div className="text-[11px] font-semibold text-gray-500 uppercase">
                                            BLEU
                                        </div>
                                        <div className="text-base font-bold text-gray-900 mt-1">
                                            {typeof output.scores.BLEU ===
                                            'number'
                                                ? output.scores.BLEU.toFixed(2)
                                                : output.scores.BLEU || '—'}
                                        </div>
                                    </div>

                                    {/* chrF */}
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                                        <div className="text-[11px] font-semibold text-gray-500 uppercase">
                                            chrF
                                        </div>
                                        <div className="text-base font-bold text-gray-900 mt-1">
                                            {typeof output.scores.chrF ===
                                            'number'
                                                ? output.scores.chrF.toFixed(2)
                                                : output.scores.chrF || '—'}
                                        </div>
                                    </div>

                                    {/* BERTScore F1 */}
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                                        <div className="text-[11px] font-semibold text-gray-500 uppercase">
                                            BERTScore F1
                                        </div>
                                        <div className="text-base font-bold text-gray-900 mt-1">
                                            {typeof output.scores[
                                                'BERTScore F1'
                                            ] === 'number'
                                                ? (
                                                      output.scores[
                                                          'BERTScore F1'
                                                      ] * 100
                                                  ).toFixed(1) + '%'
                                                : output.scores[
                                                      'BERTScore F1'
                                                  ] || '—'}
                                        </div>
                                    </div>

                                    {/* TER */}
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                                        <div className="text-[11px] font-semibold text-gray-500 uppercase flex items-center justify-center gap-1">
                                            TER
                                            <span className="text-[9px] text-gray-400 font-normal lowercase">
                                                (lower better)
                                            </span>
                                        </div>
                                        <div className="text-base font-bold text-gray-900 mt-1">
                                            {typeof output.scores.TER ===
                                            'number'
                                                ? output.scores.TER.toFixed(2)
                                                : output.scores.TER || '—'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>
                )}
            </div>
        </main>
    );
}
