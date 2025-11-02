import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_APP_URL;

export default function MyInfo() {
    const [patient, setPatient] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchPatientInfo() {
            const token = localStorage.getItem("token");
            if (!token) {
                setError("You are not logged in.");
                navigate("/login");
                return;
            }

            try {
                const res = await axios.get(`${API_BASE_URL}/patient`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setPatient(res.data);
            } catch (err) {
                console.error("❌ Failed to fetch patient info:", err);
                if (err.response?.status === 401) {
                    setError("Session expired. Please login again.");
                    localStorage.removeItem("token");
                    navigate("/login");
                } else if (err.response?.status === 403) {
                    setError("Only patients can access this page.");
                } else {
                    setError("Failed to load profile details.");
                }
            } finally {
                setLoading(false);
            }
        }

        fetchPatientInfo();
    }, [navigate]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
            <h1 className="text-3xl font-bold text-blue-600 mb-6">My Information</h1>

            {loading ? (
                <p className="text-gray-600">Loading your details...</p>
            ) : error ? (
                <p className="text-red-600 font-medium">{error}</p>
            ) : (
                <div className="bg-white shadow-lg rounded-lg p-6 w-96 text-left border border-gray-200">
                    <p className="mb-2">
                        <strong className="text-gray-700">Patient ID:</strong>{" "}
                        {patient.patient_id}
                    </p>
                    <p className="mb-2">
                        <strong className="text-gray-700">Name:</strong> {patient.name}
                    </p>
                    <p className="mb-2">
                        <strong className="text-gray-700">Email:</strong> {patient.email}
                    </p>
                    <p className="mb-2">
                        <strong className="text-gray-700">Phone:</strong> {patient.phone}
                    </p>
                </div>
            )}
        </div>
    );
}
