import { useState } from "react";
import axios from "axios";


export default function RegisterPatient() {
    const [role, setRole] = useState("patient"); // no union type here
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [specialization, setSpecialization] = useState("");
    const [phone, setPhone] = useState("");
    const [message, setMessage] = useState("");
    const API_BASE_URL = import.meta.env.VITE_API_AUTH_URL;

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                email,
                password,
                role,
                profile: { name },
            };

            if (role === "doctor") {
                payload.profile.specialization = specialization;
            }

            if (role === "patient") {
                payload.profile.phone = phone;
            }
            console.log("📡 Sending request to:", `${API_BASE_URL}/register`);
            const res = await axios.post(`${API_BASE_URL}/register`, payload);
            console.log("✅ Registered:", res.data);
            setMessage("Registration successful! You can now log in.");
        } catch (error) {
            console.error(error);
            setMessage(
                "Registration failed. " + (error.response?.data?.detail || "")
            );
        }
    };

    return (
        <div className="flex items-center justify-center h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
                <h2 className="text-2xl font-bold text-center text-blue-600 mb-6">
                    Register as {role === "doctor" ? "Doctor" : "Patient"}
                </h2>

                {/* Role Switch */}
                <div className="flex justify-center mb-6 space-x-4">
                    <button
                        className={`px-4 py-2 rounded-md font-medium ${role === "patient" ? "bg-blue-600 text-white" : "bg-gray-200"
                            }`}
                        onClick={() => setRole("patient")}
                    >
                        Patient
                    </button>
                    <button
                        className={`px-4 py-2 rounded-md font-medium ${role === "doctor" ? "bg-blue-600 text-white" : "bg-gray-200"
                            }`}
                        onClick={() => setRole("doctor")}
                    >
                        Doctor
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full p-2 border rounded-md"
                        required
                    />

                    <input
                        type="email"
                        placeholder="Email Address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-2 border rounded-md"
                        required
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 border rounded-md"
                        required
                    />

                    {role === "doctor" && (
                        <input
                            type="text"
                            placeholder="Specialization"
                            value={specialization}
                            onChange={(e) => setSpecialization(e.target.value)}
                            className="w-full p-2 border rounded-md"
                            required
                        />
                    )}
                    {role === "patient" && (
                        <input
                            type="text"
                            placeholder="Phone"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            className="w-full p-2 border rounded-md"
                            required
                        />
                    )}

                    <button
                        type="submit"
                        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
                    >
                        Register
                    </button>
                </form>

                {message && (
                    <p className="text-center mt-4 text-gray-700 font-medium">{message}</p>
                )}
            </div>
        </div>
    );
}
