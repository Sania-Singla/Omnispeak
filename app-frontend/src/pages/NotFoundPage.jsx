import { Link } from 'react-router-dom';

export default function NotFoundPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen text-white bg-slate-950">
            <h1 className="text-3xl font-bold">404 - Page Not Found</h1>
            <p className="text-center mt-6">
                The page you are looking for does not exist. Go back to the{' '}
                <Link to="/" className="text-blue-500 hover:underline">
                    home page
                </Link>
                .
            </p>
        </div>
    );
}
