import { useEffect, useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

const API_BASE_URL = import.meta.env.VITE_API_APP_URL;

export default function UpdateSlots() {
    const [slots, setSlots] = useState([]);
    const [newSlot, setNewSlot] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const token = localStorage.getItem("token");
    const doctor = token ? jwtDecode(token) : null;

    useEffect(() => {
        async function fetchDoctorSlots() {
            try {
                const res = await axios.get(`${API_BASE_URL}/doctors`);
                const data = Array.isArray(res.data) ? res.data : res.data.doctors;
                const doctorData = data?.find((d) => d.id === doctor?.sub || d.user_id === doctor?.sub);
                if (doctorData) setSlots(doctorData.available_slots || []);
            } catch (err) {
                console.error("❌ Failed to fetch doctor data:", err);
            }
        }
        fetchDoctorSlots();
    }, []);

    const generateTimeOptions = () => {
        const options = [];
        for (let h = 9; h <= 17; h++) {
            for (let m = 0; m < 60; m += 30) {
                const hour = h.toString().padStart(2, "0");
                const minute = m.toString().padStart(2, "0");
                options.push(`${hour}:${minute}`);
            }
        }
        return options;
    };

    const handleAddSlot = () => {
        if (newSlot && !slots.includes(newSlot)) {
            setSlots([...slots, newSlot]);
            setNewSlot("");
        }
    };

    const handleRemoveSlot = (slotToRemove) => {
        setSlots(slots.filter((s) => s !== slotToRemove));
    };

    const handleUpdate = async () => {
        setLoading(true);
        setMessage("");

        try {
            const payload = { available_slots: slots };
            await axios.put(`${API_BASE_URL}/doctor/slots/update`, payload, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setMessage("✅ Slots updated successfully!");
        } catch (err) {
            console.error("❌ Slot update failed:", err);
            setMessage("❌ Failed to update slots.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
            <h1 className="text-3xl font-bold text-blue-600 mb-6">
                Update Available Slots
            </h1>

            <div className="bg-white shadow-md rounded-lg p-6 w-96 border border-gray-200">
                {/* Time picker dropdown */}
                <div className="mb-4">
                    <label className="block font-medium text-gray-700 mb-1">
                        Select a Time Slot:
                    </label>
                    <div className="flex gap-2">
                        <select
                            value={newSlot}
                            onChange={(e) => setNewSlot(e.target.value)}
                            className="border p-2 rounded w-full"
                        >
                            <option value="">-- Choose Time --</option>
                            {generateTimeOptions().map((t) => (
                                <option key={t} value={t}>
                                    {t}
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={handleAddSlot}
                            className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
                        >
                            Add
                        </button>
                    </div>
                </div>

                {/* Display selected slots */}
                <ul className="mb-4 max-h-40 overflow-y-auto">
                    {slots.map((slot, idx) => (
                        <li
                            key={idx}
                            className="flex justify-between items-center bg-gray-100 px-3 py-1 mb-2 rounded"
                        >
                            {slot}
                            <button
                                onClick={() => handleRemoveSlot(slot)}
                                className="text-red-600 hover:text-red-800"
                            >
                                ✕
                            </button>
                        </li>
                    ))}
                </ul>

                {/* Submit */}
                <button
                    onClick={handleUpdate}
                    disabled={loading}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 w-full"
                >
                    {loading ? "Updating..." : "Update Slots"}
                </button>

                {message && (
                    <p
                        className={`mt-3 text-center font-medium ${message.startsWith("✅") ? "text-green-600" : "text-red-600"
                            }`}
                    >
                        {message}
                    </p>
                )}
            </div>
        </div>
    );
}
