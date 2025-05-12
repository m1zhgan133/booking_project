import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import BookingSystem from './pages/Home';
import Registration from './pages/Registration';
import ThankYou from './pages/Thank-you';
import Admin from './pages/Admin';

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<BookingSystem />} />
                <Route path="/registration" element={<Registration />} />
                <Route path="/thank-you" element={<ThankYou />} />
                <Route path="/admin" element={<Admin />} />
            </Routes>
        </Router>
    );
}