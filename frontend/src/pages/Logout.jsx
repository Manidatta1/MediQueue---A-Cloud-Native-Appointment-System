import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        // ✅ Clear session data
        localStorage.removeItem("token");

        // ✅ Optional: clear any cached user data if stored
        sessionStorage.clear();

        // Redirect after short delay
        const timer = setTimeout(() => {
            navigate("/login");
        }, 2000);

        return () => clearTimeout(timer);
    }, [navigate]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
            <h1 className="text-3xl font-bold text-blue-600 mb-4">
                Logging you out...
            </h1>
            <p className="text-gray-600">Please wait, redirecting to login page.</p>
        </div>
    );
}
