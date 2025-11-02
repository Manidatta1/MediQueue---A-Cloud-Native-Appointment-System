import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Doctors from "./pages/Doctors";
import RegisterPatient from "./pages/RegisterPatient";
import BookAppointment from "./pages/BookAppointment";
import MyInfo from "./pages/MyInfo";
import Login from "./pages/Login";
import Navbar from "./components/Navbar";
import Logout from "./pages/Logout";
import UpdateSlots from "./pages/UpdateSlots";

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/doctors" element={<Doctors />} />
        <Route path="/register" element={<RegisterPatient />} />
        <Route path="/book" element={<BookAppointment />} />
        <Route path="/myinfo" element={<MyInfo />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/update-slots" element={<UpdateSlots />} />
      </Routes>
    </Router>
  );
}
