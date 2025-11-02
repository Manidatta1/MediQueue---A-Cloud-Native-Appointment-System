import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [role, setRole] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            setIsLoggedIn(true);
            try {
                const decoded = jwtDecode(token);
                setRole(decoded.role);
            } catch (error) {
                console.error("❌ Failed to decode token:", error);
            }
        } else {
            setIsLoggedIn(false);
            setRole(null);
        }
    }, [location]);

    const handleLogout = () => {
        localStorage.removeItem("token");
        sessionStorage.clear();
        setIsLoggedIn(false);
        setRole(null);
        navigate("/login");
    };

    const active = (path) =>
        location.pathname === path
            ? "text-blue-600 font-semibold border-b-2 border-blue-600 pb-1"
            : "text-gray-700 hover:text-blue-500 transition";

    return (
        <nav className="bg-white shadow-md fixed top-0 left-0 w-full z-50">
            <div className="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
                <Link
                    to="/"
                    className="text-2xl font-extrabold text-blue-600 flex items-center gap-2"
                >
                    🏥 <span>HealthCare</span>
                </Link>

                <div className="flex gap-8 text-lg items-center">
                    <Link to="/" className={active("/")}>
                        Home
                    </Link>
                    <Link to="/doctors" className={active("/doctors")}>
                        Doctors
                    </Link>

                    {!isLoggedIn && (
                        <Link to="/register" className={active("/register")}>
                            Register
                        </Link>
                    )}

                    {/* ✅ Patient Links */}
                    {isLoggedIn && role === "patient" && (
                        <>
                            <Link to="/book" className={active("/book")}>
                                Book
                            </Link>
                            <Link to="/myinfo" className={active("/myinfo")}>
                                My Info
                            </Link>
                        </>
                    )}

                    {/* ✅ Doctor Links */}
                    {isLoggedIn && role === "doctor" && (
                        <Link to="/update-slots" className={active("/update-slots")}>
                            Update Slots
                        </Link>
                    )}

                    {/* ✅ Conditional Login / Logout */}
                    {isLoggedIn ? (
                        <button
                            onClick={handleLogout}
                            className="text-red-600 hover:text-red-700 font-semibold transition"
                        >
                            Logout
                        </button>
                    ) : (
                        <Link to="/login" className={active("/login")}>
                            Login
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}
