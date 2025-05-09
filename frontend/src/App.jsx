import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import BookingSystem from './pages/Home';
import Registration from './pages/Registration';
import ThankYou from './pages/Thank-you';

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<BookingSystem />} />
                <Route path="/registration" element={<Registration />} />
                <Route path="/thank-you" element={<ThankYou />} />
            </Routes>
        </Router>
    );
}