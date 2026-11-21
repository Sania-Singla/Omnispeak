import { useNavigate } from 'react-router-dom';
import { useUser } from './contexts/UserContext';
import { LANGUAGES } from './constants';

export default function App() {
    const navigate = useNavigate();
    const { user, setUser } = useUser();

    return (
        <div className="min-h-screen bg-slate-950 text-white flex flex-col gap-8 items-center justify-center px-6">
            <h1 className="text-3xl font-bold">OmniSpeak</h1>

            <form
                onSubmit={(e) => {
                    e.preventDefault();
                    navigate(`/chat`);
                }}
                className="flex flex-col gap-6 w-full max-w-sm"
            >
                {/* name input */}
                <div className="flex flex-col">
                    <label htmlFor="name" className="font-medium mb-2">
                        Enter your name
                    </label>
                    <input
                        type="text"
                        id="name"
                        onChange={(e) =>
                            setUser({ ...user, name: e.target.value })
                        }
                        value={user?.name || ''}
                        required
                        className="w-full bg-slate-800 border border-slate-600 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Your name"
                    />
                </div>

                {/* language selector */}
                <div className="flex flex-col">
                    <label htmlFor="language" className="font-medium mb-2">
                        Select your language
                    </label>
                    <select
                        id="language"
                        onChange={(e) =>
                            setUser({ ...user, language: e.target.value })
                        }
                        required
                        className="w-full bg-slate-800 border border-slate-600 rounded-md py-2 px-3"
                    >
                        {Object.entries(LANGUAGES).map(([code, name]) => (
                            <option key={code} value={code}>
                                {name}
                            </option>
                        ))}
                    </select>
                </div>

                <button
                    type="submit"
                    className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition cursor-pointer"
                >
                    Start Chat
                </button>
            </form>
        </div>
    );
}
