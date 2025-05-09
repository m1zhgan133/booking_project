import React, { useState } from 'react';

export default function BookingSystem() {
    // Состояния для проверки свободности мест
    const [startTime, setStartTime] = useState("2025-04-30T14:30");
    const [endTime, setEndTime] = useState("2025-04-30T15:30");
    const [seatsStatus, setSeatsStatus] = useState(Array(20).fill(null));

    // Состояния для формы бронирования
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [bookingStartTime, setBookingStartTime] = useState("2025-04-30T14:30");
    const [duration, setDuration] = useState("01:00");
    const [seatNumber, setSeatNumber] = useState("");
    const [errors, setErrors] = useState({});
    const [successMessage, setSuccessMessage] = useState("");

    const checkAvailability = async () => {
        try {
            const response = await fetch(`/api/check_availability?start=${startTime}&end=${endTime}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error ||'Ошибка при получении данных');
            }

            const data = await response.json();
            const newStatus = [...seatsStatus]; // копируем
            for (let i = 1; i < 21; i++) {
                newStatus[i-1] = data.seats[i] ? "Свободно" : "Занято";
            }
            setSeatsStatus(newStatus); //обновляем
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при проверке мест");
        }
    };

    const handleBooking = async () => {
        // проверяем все ли поля заполненны, если не заполненно подсвечиваем красным
        const newErrors = {
            username: !username,
            password: !password,
            bookingStartTime: !bookingStartTime,
            duration: !duration,
            seatNumber: !seatNumber
        };

        // Проверяем, есть ли true
        const hasErrors = Object.values(newErrors).some(Boolean);
        if (hasErrors) {
            setErrors(newErrors);
            return;
        }
        setErrors({}); // Сброс ошибок

        try {
            const response = await fetch('/api/booking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    st_datetime: bookingStartTime,
                    duration: duration,
                    id_place: seatNumber
                })
            });

            if (response.status === 201) {
                setSuccessMessage("Запись успешно создана");
                setTimeout(() => setSuccessMessage(""), 10000); // Сообщение исчезнет через 10 секунд
                // Сброс формы после бронирования
                setUsername("");
                setPassword("");
                setSeatNumber("");
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Произошла ошибка при бронировании");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при бронировании");
        }
    };

    return (
        <div>
            {/*// сообщение успешное бронирование*/}
            {/* если successMessage не пустая строка, то возвращается то, что после && */}
            {successMessage && (
                <div style={{
                    position: 'fixed',
                    top: '10px',
                    left: '10px',
                    backgroundColor: 'green',
                    color: 'white',
                    padding: '10px',
                    borderRadius: '5px',
                    zIndex: 1000
                }}>
                    {successMessage}
                </div>
            )}

            {/* блок проверки доступности мест */}
            <div className="big-box">
                <h1>Бронирование мест в коворкинге</h1>
            </div>

            <div className="big-box">
                <h2>Посмотреть свободные места</h2>
            </div>

            <div className="input-container">
                <label htmlFor="start-time">Начальное время</label>
                <input
                    type="datetime-local"
                    id="start-time"
                    name="start-time"
                    value={startTime}
                    min="2025-04-01T00:00"
                    max="2025-12-31T23:59"
                    step="900"
                    onChange={(e) => setStartTime(e.target.value)}
                />

                <label htmlFor="end-time">Конечное время</label>
                <input
                    type="datetime-local"
                    id="end-time"
                    name="end-time"
                    value={endTime}
                    min={startTime}
                    max="2025-12-31T23:59"
                    step="900"
                    onChange={(e) => setEndTime(e.target.value)}
                />

                <button
                    id="check-booking-button"
                    onClick={checkAvailability}
                >
                    Проверить доступность
                </button>

                <div className="tables-container">
                    <table className="data-table">
                        <thead>
                        <tr>
                            <th className="column-header">Место</th>
                            <th className="column-header">Доступно</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Array.from({length: 10}, (_, i) => i + 1).map(seat => (
                            <tr key={`seat-${seat}`} id={`seat-${seat}`}>
                                <td>{seat}</td>
                                <td>{seatsStatus[seat-1] || "-"}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                    <table className="data-table">
                        <thead>
                        <tr>
                            <th className="column-header">Место</th>
                            <th className="column-header">Доступно</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Array.from({length: 10}, (_, i) => i + 11).map(seat => (
                            <tr key={`seat-${seat}`} id={`seat-${seat}`}>
                                <td>{seat}</td>
                                <td>{seatsStatus[seat-1] || "-"}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Секция бронирования */}
            <div>
                <div className="big-box">
                    <h2>Забронировать место</h2>
                </div>
                <div className="input-container" id="booking-inputs-title">
                    <label>Введите ваш username</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        placeholder="Введите username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{ borderColor: errors.username ? 'red' : '' }}
                    />

                    <label>Введите ваш пароль</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        placeholder="Введите пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ borderColor: errors.password ? 'red' : '' }}
                    />

                    <label>Выберите место (1-20)</label>
                    <input
                        type="number"
                        id="seat-number"
                        name="seat-number"
                        placeholder="Номер места (1-20)"
                        min="1"
                        max="20"
                        value={seatNumber}
                        onChange={(e) => setSeatNumber(e.target.value)}
                        style={{ borderColor: errors.seatNumber ? 'red' : '' }}
                    />

                    <label>Выберите дату и время начала брони</label>
                    <input
                        type="datetime-local"
                        name="st-time"
                        id="st-time"
                        value={bookingStartTime}
                        min="2025-04-01T00:00"
                        max="2025-12-31T23:59"
                        step="900"
                        onChange={(e) => setBookingStartTime(e.target.value)}
                    />

                    <label>Выберите длительность брони</label>
                    <input
                        type="time"
                        name="duration"
                        id="duration"
                        value={duration}
                        min="00:00"
                        max="23:59"
                        step="900"
                        onChange={(e) => setDuration(e.target.value)}
                    />

                    <button id="booking-button" onClick={handleBooking}>Забронировать</button>
                </div>
                <button id="registration-button">Зарегистрироваться</button>
            </div>
        </div>
    );
}