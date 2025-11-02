import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_APP_URL;

export default function Doctors() {
    const [doctors, setDoctors] = useState([]);
    const [specializations, setSpecializations] = useState([]);
    const [selectedSpec, setSelectedSpec] = useState("");
    const [searchName, setSearchName] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ✅ Fetch all doctors + specializations on mount
    useEffect(() => {
        async function fetchInitialData() {
            try {
                setLoading(true);
                const [doctorsRes, specRes] = await Promise.all([
                    axios.get(`${API_BASE_URL}/doctors`),
                    axios.get(`${API_BASE_URL}/doctor/specializations`)
                ]);
                setDoctors(doctorsRes.data);
                setSpecializations(specRes.data);
            } catch (err) {
                console.error("❌ Failed to load doctors:", err);
                setError("Failed to load doctors.");
            } finally {
                setLoading(false);
            }
        }
        fetchInitialData();
    }, []);

    // ✅ Handle search/filter
    const handleSearch = async () => {
        try {
            setLoading(true);
            setError("");

            const params = {};
            if (selectedSpec) params.specialization = selectedSpec;
            if (searchName) params.name = searchName;

            const res = await axios.get(`${API_BASE_URL}/doctor/search`, { params });
            setDoctors(res.data);
        } catch (err) {
            if (err.response?.status === 404) {
                setDoctors([]);
                setError("No matching doctors found.");
            } else {
                setError("Search failed. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    const resetFilters = async () => {
        setSelectedSpec("");
        setSearchName("");
        setError("");
        const res = await axios.get(`${API_BASE_URL}/doctors`);
        setDoctors(res.data);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <h1 className="text-3xl font-bold text-blue-600 mb-6 text-center">
                Find a Doctor
            </h1>

            {/* 🔍 Filters */}
            <div className="flex flex-wrap gap-4 justify-center mb-8">
                <select
                    className="border border-gray-300 rounded-lg p-2 w-52"
                    value={selectedSpec}
                    onChange={(e) => setSelectedSpec(e.target.value)}
                >
                    <option value="">All Specializations</option>
                    {specializations.map((spec) => (
                        <option key={spec} value={spec}>{spec}</option>
                    ))}
                </select>

                <input
                    type="text"
                    placeholder="Search by name"
                    className="border border-gray-300 rounded-lg p-2 w-52"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                />

                <button
                    onClick={handleSearch}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                    Search
                </button>

                <button
                    onClick={resetFilters}
                    className="bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold hover:bg-gray-500 transition"
                >
                    Reset
                </button>
            </div>

            {/* 🩺 Doctor List */}
            {loading ? (
                <p className="text-center text-gray-600">Loading doctors...</p>
            ) : error ? (
                <p className="text-center text-red-600">{error}</p>
            ) : doctors.length === 0 ? (
                <p className="text-center text-gray-600">No doctors found.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {doctors.map((doc) => (
                        <div
                            key={doc.id}
                            className="bg-white shadow-lg rounded-lg p-6 border border-gray-200 hover:shadow-xl transition"
                        >
                            <h2 className="text-xl font-semibold text-blue-600 mb-2">
                                {doc.name}
                            </h2>
                            <p className="text-gray-700 mb-1">
                                <strong>Specialization:</strong> {doc.specialization}
                            </p>
                            <p className="text-gray-700 mb-1">
                                <strong>Available Slots:</strong> {doc.available_slots?.join(", ") || "None"}
                            </p>
                            <p className="text-gray-700 mb-1">
                                <strong>Daily Limit:</strong> {doc.daily_limit}
                            </p>
                            <p className="text-gray-700">
                                <strong>Booked:</strong> {doc.booked_slots}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
