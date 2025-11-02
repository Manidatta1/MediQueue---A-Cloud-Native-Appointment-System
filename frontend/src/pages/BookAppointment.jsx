import { useEffect, useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";


const API_BASE_URL = import.meta.env.VITE_API_APP_URL;

export default function BookAppointment() {
    const [doctors, setDoctors] = useState([]);
    const [selectedDoctor, setSelectedDoctor] = useState("");
    const [selectedTime, setSelectedTime] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    const token = localStorage.getItem("token");
    const user = token ? jwtDecode(token) : null;

    // ✅ Fetch doctors on page load
    useEffect(() => {
        async function fetchDoctors() {
            try {
                const res = await axios.get(`${API_BASE_URL}/doctors`);
                setDoctors(res.data);
            } catch (err) {
                console.error("❌ Failed to fetch doctors:", err);
            }
        }
        fetchDoctors();
    }, []);

    // ✅ Handle booking
    const handleBook = async () => {
        if (!selectedDoctor || !selectedTime) {
            setMessage("⚠️ Please select both a doctor and a time slot.");
            return;
        }

        try {
            setLoading(true);
            setMessage("");

            const payload = {
                doctor_id: parseInt(selectedDoctor),
                time: selectedTime,
            };

            console.log("📤 Booking payload:", payload);

            const res = await axios.post(`${API_BASE_URL}/book`, null, {
                params: payload, // backend expects query params
                headers: { Authorization: `Bearer ${token}` },
            });

            setMessage(`✅ ${res.data.message}`);
        } catch (err) {
            console.error("❌ Booking failed:", err);
            if (err.response?.data?.detail) {
                setMessage(`❌ ${err.response.data.detail}`);
            } else {
                setMessage("❌ Failed to book appointment.");
            }
        } finally {
            setLoading(false);
        }
    };

    // ✅ UI Rendering
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
            <h1 className="text-3xl font-bold text-blue-600 mb-6">Book Appointment</h1>

            {/* Doctor Selection */}
            <div className="w-full max-w-md mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                    Select Doctor:
                </label>
                <select
                    value={selectedDoctor}
                    onChange={(e) => setSelectedDoctor(e.target.value)}
                    className="w-full border p-2 rounded"
                >
                    <option value="">-- Choose a doctor --</option>
                    {doctors.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                            {doc.name} ({doc.specialization})
                        </option>
                    ))}
                </select>
            </div>

            {/* Slot Selection */}
            {selectedDoctor && (
                <div className="w-full max-w-md mb-4">
                    <label className="block text-gray-700 font-semibold mb-2">
                        Select Time Slot:
                    </label>
                    <select
                        value={selectedTime}
                        onChange={(e) => setSelectedTime(e.target.value)}
                        className="w-full border p-2 rounded"
                    >
                        <option value="">-- Choose a slot --</option>
                        {doctors
                            .find((d) => d.id === parseInt(selectedDoctor))
                            ?.available_slots?.map((slot) => (
                                <option key={slot} value={slot}>
                                    {slot}
                                </option>
                            ))}
                    </select>
                </div>
            )}

            {/* Book Button */}
            <button
                onClick={handleBook}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
            >
                {loading ? "Booking..." : "Book Appointment"}
            </button>

            {/* Message */}
            {message && (
                <p className="mt-4 text-center font-semibold text-gray-700">{message}</p>
            )}
        </div>
    );
}
