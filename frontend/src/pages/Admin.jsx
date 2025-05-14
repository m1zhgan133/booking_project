import React, {useRef, useState} from 'react';
import {Link} from "react-router-dom";

export default function Admin() {
    // Состояния для проверки свободности мест
    const [startTime, setStartTime] = useState("2025-04-30T14:30");
    const [endTime, setEndTime] = useState("2025-04-30T15:30");
    const [seatsStatus, setSeatsStatus] = useState(Array(20).fill(null));

    //Состояния для авторизации
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userId, setUserId] = useState(""); // новое, не из этого файла
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const authDataRef = useRef({
        username: '',
        password: ''
    });

    // для выбора меню
    const [isUserMenu, setIsUserMenu] = useState(false); // Иначе booking menu

    // Состояния для формы бронирования
    const [bookingStartTime, setBookingStartTime] = useState("2025-04-30T14:30");
    const [duration, setDuration] = useState("01:00");
    const [seatNumber, setSeatNumber] = useState("");
    const [errors, setErrors] = useState({});
    const [successMessage, setSuccessMessage] = useState("");

    // Состояние для карточек с инфой о бронях
    const [userBookings, setUserBookings] = useState([]);
    // Состояния для кнопки изменить в карточках
    const [editingBookingId, setEditingBookingId] = useState(0);

    // Для кнопки изменить
    const [checkboxes, setCheckboxes] = useState({
        place: false,
        start: false,
        duration: false
    });
    const [formData, setFormData] = useState({
        place: '',
        start: "2025-04-30T14:30",
        duration: "01:00"
    });

    const checkAvailability = async () => {
        try {
            const response = await fetch(`/api/booking?start=${startTime}&end=${endTime}&request_type=range`);
            if (response.ok) {
                const data = await response.json();
                const newStatus = [...seatsStatus]; // копируем
                for (let i = 1; i < 21; i++) {
                    newStatus[i-1] = data.seats[i] ? "Свободно" : "Занято";
                }
                setSeatsStatus(newStatus); //обновляем
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error ||'Ошибка при получении данных');
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при проверке мест");
        }
    };

    const auth = async () => {
        const newErrors = {
            username: !username,
            password: !password
        }
        // Проверяем, есть ли true
        const hasErrors = Object.values(newErrors).some(Boolean);
        if (hasErrors) {
            setErrors(newErrors);
            return;
        }
        setErrors({}); // Сброс ошибок

        try {
            const response = await fetch("/api/is_admin", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                authDataRef.current = {username, password};
                setSuccessMessage("Вы успешно авторизовались как админ");
                setTimeout(() => setSuccessMessage(""), 10000); // Сообщение исчезнет через 10 секунд
                // Сброс формы после бронирования
                setUsername("");
                setPassword("");
                setIsLoggedIn(true);
                fetchUserBookings();
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Произошла ошибка при авторизации под записью админа, вы ввели некорректные данные");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при авторизации под записью админа");
        }
    }

const handleBooking = async () => {
        // проверяем все ли поля заполненны, если не заполненно подсвечиваем красным
    const newErrors = {
        userId: !userId,
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
                username: authDataRef.current.username,
                password: authDataRef.current.password,
                st_datetime: bookingStartTime,
                duration: duration,
                id_place: seatNumber,
                user_id: userId,
            })
        });

        if (response.ok) {
            setSuccessMessage("Запись успешно создана");
                setTimeout(() => setSuccessMessage(""), 10000); // Сообщение исчезнет через 10 секунд
                // Сброс формы после бронирования
            setSeatNumber("");
            setUserId("");
            await fetchUserBookings();
        } else {
            const errorData = await response.json();
            alert(errorData.error || "Произошла ошибка при бронировании");
        }
    } catch (error) {
        console.error("Ошибка:", error);
        alert("Произошла ошибка при бронировании");
    }
};
    // ---------------------------- Информация о бронированиях ----------------------------
    const fetchUserBookings = async () => {
        try {
            const response = await fetch(`/api/user?username=${authDataRef.current.username}&password=${authDataRef.current.password}&request_type=all`, {
                method: 'GET'
            });

            if (response.ok) {
                const data = await response.json();
                setUserBookings(data || []);
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Ошибка при загрузке бронирований");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Не удалось загрузить бронирования");
        }
    };

    // Форматирование даты и времени убираем секунды
    const formatDateTime = (datetime) => {
        const options = {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        };
        return new Date(datetime).toLocaleString('ru-RU', options);
    };

    const formatDuration = (minutes) => {
        const hours = Math.floor(Math.abs(minutes) / 60);
        const mins = Math.abs(minutes) % 60;

        // Добавляем ведущий ноль
        const pad = (num) => num.toString().padStart(2, '0');
        return `${pad(hours)}:${pad(mins)}`;
    }


// Функции для кнопок
    const handleCancel = async (bookingId) => {
        try {
            const response = await fetch(`/api/booking`, {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: authDataRef.current.username,
                    password: authDataRef.current.password,
                    booking_id: bookingId,
                })
            })

            if (response.ok) {
                setUserBookings(userBookings.filter(booking => booking.id !== bookingId));
                setSuccessMessage("Бронирование отменено");
                setTimeout(() => setSuccessMessage(""), 5000);
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Произошла ошибка при отмене бронирования");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Не удалось отменить бронирование");
        }
    }


    const handleEdit = (bookingId, IdPlace, stDatetime, duration) => {
        if (bookingId === editingBookingId) {
            setEditingBookingId(0)
        } else {
            setFormData({
                place: IdPlace,
                start: stDatetime.replace(' ', 'T'),
                duration: formatDuration(duration) // Конвертируем минуты в HH:MM
            });
            setCheckboxes({
                place: false,
                start: false,
                duration: false
            })
            setEditingBookingId(bookingId);
        }
    };


    const handleCheckboxChange = (e) => {
        const { name, checked } = e.target;
        setCheckboxes(prev => ({
            ...prev,
            [name]: checked
        }));
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async () => {
        try {
            // Формируем данные только для отмеченных полей
            const dataToSend = {
                username: authDataRef.current.username,
                password: authDataRef.current.password,
                booking_id: editingBookingId,
                place: formData.place,
                start: formData.start,
                duration: formData.duration
            };


            // Отправка на бэкенд
            const response = await fetch('/api/booking', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                setSuccessMessage("Запись успешно изменена");
                setTimeout(() => setSuccessMessage(""), 10000); // Сообщение исчезнет через 10 секунд

                // Сбрасываем состояние редактирования
                setEditingBookingId(0);
                setCheckboxes({
                    place: false,
                    start: false,
                    duration: false
                });
                setFormData({
                    place: '',
                    start: "2025-04-30T14:30",
                    duration: "01:00"
                });
                await fetchUserBookings();
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Произошла ошибка при редактировании бронирования");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при редактировании бронирования");
        }
    };

    // ----------------------------------------------- Пользователи --------------------------------------------------------
    // const [usersList, setUsersList] = useState([]);
    //
    // const fetchUsers = async () => {
    //     try {
    //         const response = await fetch(`/api/users?username=${authDataRef.current.username}&password=${authDataRef.current.password}`, {
    //             method: 'GET'
    //         });
    //
    //         if (response.ok) {
    //             const data = await response.json();
    //             setUsersList(data || []);
    //         } else {
    //             const errorData = await response.json();
    //             alert(errorData.error || "Ошибка при загрузке пользователей");
    //         }
    //     } catch (error) {
    //         console.error("Ошибка:", error);
    //         alert("Не удалось загрузить список пользователей");
    //     }
    // };



    return (
        <div>
            {/*// сообщение успешное бронирование*/}
            {/* если successMessage не пустая строка, то возвращается то, что после && */}
            {successMessage && (
                <div className={'success-message'}>
                    {successMessage}
                </div>
            )}

            {/* блок проверки доступности мест */}
            <div className="big-box">
                <h1>Админская панель</h1>
            </div>



            {!isLoggedIn ? (
                <div>
                    <div className="big-box">
                        <h2>Авторизация</h2>
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
                            style={{ boxShadow: errors.username
                                    ? '0 0 0 2px red'
                                    : '0 4px 8px rgba(0, 0, 0, 0.2)'}}
                        />

                        <label>Введите ваш пароль</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            placeholder="Введите пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ boxShadow: errors.password
                                    ? '0 0 0 2px red'
                                    : '0 4px 8px rgba(0, 0, 0, 0.2)'}}
                        />
                        <button id="auth-button" onClick={auth}>Авторизоваться</button>
                    </div>
                    <Link to="/registration">
                        <button id="to-registration-button">Зарегистрироваться</button>
                    </Link>
                </div>
            ) : (
                <div>
                <div className="input-container">
                    <div>
                        <button onClick={() => setIsUserMenu(false)}
                                style={{border: !isUserMenu ? '3px solid black' : 'none',}}>Бронирования</button>
                        <button onClick={() => setIsUserMenu(true)}
                                style={{border: isUserMenu ? '3px solid black' : 'none',}}>Пользователи</button>
                    </div>
                </div>
                    {!isUserMenu ? (
                        <div> {/*  начало контейнира содержащего все что доступно после авторизации */}
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
                                            <label>ID пользователя</label>
                                            <input
                                                type="text"
                                                id="user-id"
                                                name="user-id"
                                                placeholder="Введите ID пользователя"
                                                value={userId}
                                                onChange={(e) => setUserId(e.target.value)}
                                                style={{ boxShadow: errors.userId
                                                        ? '0 0 0 2px red'
                                                        : '0 4px 8px rgba(0, 0, 0, 0.2)'}}
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
                                                style={{ boxShadow: errors.seatNumber
                                                        ? '0 0 0 2px red'
                                                        : '0 4px 8px rgba(0, 0, 0, 0.2)'}}
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
                                    </div>

                                    {/* Секция информации о бронях пользователей */}
                                    <div>
                                        <div className="big-box">
                                            <h2>Все бронирования</h2>
                                        </div>

                                        {userBookings.length > 0 ? (
                                            <div className="booking-container">
                                                {userBookings.map((booking) => (
                                                    <React.Fragment key={booking.id}>
                                                        <div className="booking-card">
                                                            <h3>Информация о брони {booking.id}</h3>
                                                            <div className="booking-info">
                                                                <p><span>ID пользователя:</span> {booking.id_user}</p>
                                                                <p><span>Место:</span> {booking.id_place}</p>
                                                                <p><span>Начало:</span> {formatDateTime(booking.st_datetime)}</p>
                                                                <p><span>Окончание:</span> {formatDateTime(booking.en_datetime)}</p>
                                                                <p><span>Продолжительность:</span> {booking.duration} минут</p>
                                                            </div>
                                                            <div className="booking-actions">
                                                                <button
                                                                    className="cancel-btn"
                                                                    onClick={() => handleCancel(booking.id)}>Отменить</button>
                                                                <button
                                                                    className="edit-btn"
                                                                    onClick={() => handleEdit(booking.id, booking.id_place,
                                                                        booking.st_datetime, booking.duration)}>
                                                                    {editingBookingId === booking.id ? 'Закрыть' : 'Изменить'}
                                                                </button>
                                                            </div>
                                                        </div>
                                                        {editingBookingId === booking.id && (
                                                            <div className="edit-container">
                                                                <h3>Редактирование брони {booking.id}</h3>
                                                                {/* Первая строка - галочки */}
                                                                <div className="checkbox-row">
                                                                    <label className="checkbox-label">
                                                                        <input
                                                                            type="checkbox"
                                                                            name="place"
                                                                            checked={checkboxes.place}
                                                                            onChange={handleCheckboxChange}
                                                                        />
                                                                        Место
                                                                    </label>

                                                                    <label className="checkbox-label">
                                                                        <input
                                                                            type="checkbox"
                                                                            name="start"
                                                                            checked={checkboxes.start}
                                                                            onChange={handleCheckboxChange}
                                                                        />
                                                                        Начало
                                                                    </label>

                                                                    <label className="checkbox-label">
                                                                        <input
                                                                            type="checkbox"
                                                                            name="duration"
                                                                            checked={checkboxes.duration}
                                                                            onChange={handleCheckboxChange}
                                                                        />
                                                                        Длительность
                                                                    </label>
                                                                </div>

                                                                {/* Вторая строка - блоки ввода */}
                                                                <div className="input-row">
                                                                    {checkboxes.place && (
                                                                        <div className="input-block">
                                                                            <label>Место(1-20):</label>
                                                                            <input
                                                                                type="number"
                                                                                name="place"
                                                                                placeholder="Номер"
                                                                                min="1"
                                                                                max="20"
                                                                                value={formData.place}
                                                                                onChange={handleInputChange}
                                                                            />
                                                                        </div>
                                                                    )}

                                                                    {checkboxes.start && (
                                                                        <div className="input-block">
                                                                            <label>Начало:</label>
                                                                            <input
                                                                                type="datetime-local"
                                                                                name="start"
                                                                                value={formData.start}
                                                                                min="2025-04-01T00:00"
                                                                                max="2025-12-31T23:59"
                                                                                step="900"
                                                                                onChange={handleInputChange}
                                                                            />
                                                                        </div>
                                                                    )}

                                                                    {checkboxes.duration && (
                                                                        <div className="input-block">
                                                                            <label>Длительность:</label>
                                                                            <input
                                                                                type="time"
                                                                                name="duration"
                                                                                value={formData.duration}
                                                                                min="00:00"
                                                                                max="23:59"
                                                                                step="900"
                                                                                onChange={handleInputChange}
                                                                            />
                                                                        </div>
                                                                    )}
                                                                </div>
                                                                {/* 3 строка - ввод*/}
                                                                <button className="edit-btn"
                                                                        onClick={handleSubmit}>Отредактировать</button>
                                                            </div>
                                                        )}
                                                    </React.Fragment>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className={'input-container'}><p className="no-bookings">У вас нет активных бронирований</p></div>
                                        )}
                                    </div>

                                </div> // конец контейнера, содержащего все что доступно после авторизации в одной из вкладок
                        ) : (
                        <div>
                            {/* Секция информации о пользователях */}
                            <div>
                                <div className="big-box">
                                    <h2>Все пользователи</h2>
                                </div>

                                {userBookings.length > 0 ? (
                                    <div className="booking-container">
                                        {userBookings.map((booking) => (
                                            <React.Fragment key={booking.id}>
                                                <div className="booking-card">
                                                    <h3>Информация о брони {booking.id}</h3>
                                                    <div className="booking-info">
                                                        <p><span>ID пользователя:</span> {booking.id_user}</p>
                                                        <p><span>Место:</span> {booking.id_place}</p>
                                                        <p><span>Начало:</span> {formatDateTime(booking.st_datetime)}</p>
                                                        <p><span>Окончание:</span> {formatDateTime(booking.en_datetime)}</p>
                                                        <p><span>Продолжительность:</span> {booking.duration} минут</p>
                                                    </div>
                                                    <div className="booking-actions">
                                                        <button
                                                            className="cancel-btn"
                                                            onClick={() => handleCancel(booking.id)}>Отменить</button>
                                                        <button
                                                            className="edit-btn"
                                                            onClick={() => handleEdit(booking.id, booking.id_place,
                                                                booking.st_datetime, booking.duration)}>
                                                            {editingBookingId === booking.id ? 'Закрыть' : 'Изменить'}
                                                        </button>
                                                    </div>
                                                </div>
                                                {editingBookingId === booking.id && (
                                                    <div className="edit-container">
                                                        <h3>Редактирование брони {booking.id}</h3>
                                                        {/* Первая строка - галочки */}
                                                        <div className="checkbox-row">
                                                            <label className="checkbox-label">
                                                                <input
                                                                    type="checkbox"
                                                                    name="place"
                                                                    checked={checkboxes.place}
                                                                    onChange={handleCheckboxChange}
                                                                />
                                                                Место
                                                            </label>

                                                            <label className="checkbox-label">
                                                                <input
                                                                    type="checkbox"
                                                                    name="start"
                                                                    checked={checkboxes.start}
                                                                    onChange={handleCheckboxChange}
                                                                />
                                                                Начало
                                                            </label>

                                                            <label className="checkbox-label">
                                                                <input
                                                                    type="checkbox"
                                                                    name="duration"
                                                                    checked={checkboxes.duration}
                                                                    onChange={handleCheckboxChange}
                                                                />
                                                                Длительность
                                                            </label>
                                                        </div>

                                                        {/* Вторая строка - блоки ввода */}
                                                        <div className="input-row">
                                                            {checkboxes.place && (
                                                                <div className="input-block">
                                                                    <label>Место(1-20):</label>
                                                                    <input
                                                                        type="number"
                                                                        name="place"
                                                                        placeholder="Номер"
                                                                        min="1"
                                                                        max="20"
                                                                        value={formData.place}
                                                                        onChange={handleInputChange}
                                                                    />
                                                                </div>
                                                            )}

                                                            {checkboxes.start && (
                                                                <div className="input-block">
                                                                    <label>Начало:</label>
                                                                    <input
                                                                        type="datetime-local"
                                                                        name="start"
                                                                        value={formData.start}
                                                                        min="2025-04-01T00:00"
                                                                        max="2025-12-31T23:59"
                                                                        step="900"
                                                                        onChange={handleInputChange}
                                                                    />
                                                                </div>
                                                            )}

                                                            {checkboxes.duration && (
                                                                <div className="input-block">
                                                                    <label>Длительность:</label>
                                                                    <input
                                                                        type="time"
                                                                        name="duration"
                                                                        value={formData.duration}
                                                                        min="00:00"
                                                                        max="23:59"
                                                                        step="900"
                                                                        onChange={handleInputChange}
                                                                    />
                                                                </div>
                                                            )}
                                                        </div>
                                                        {/* 3 строка - ввод*/}
                                                        <button className="edit-btn"
                                                                onClick={handleSubmit}>Отредактировать</button>
                                                    </div>
                                                )}
                                            </React.Fragment>
                                        ))}
                                    </div>
                                ) : (
                                    <div className={'input-container'}><p className="no-bookings">У вас нет активных бронирований</p></div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}

        </div>
    );
}