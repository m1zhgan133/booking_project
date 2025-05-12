import React, {useRef, useState} from "react";
import {Link} from "react-router-dom";


export default function Admin() {
    // Состоянния для событий успеха и ошибок
    const [errors, setErrors] = useState({});
    const [successMessage, setSuccessMessage] = useState("");

    //Состояния для авторизации
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const authDataRef = useRef({
        username: '',
        password: ''
    });

    // Состояние для карточек с инфой о бронях пользователя
    const [bookings, setBookings] = useState([]);


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
            const isAdminUsername = username === adminUsername;
            const isAdminPassword = password === adminPassword;

            if (isAdminUsername && isAdminPassword) {
                authDataRef.current = {username, password};
                setSuccessMessage("Вы успешно авторизовались как админ");
                setTimeout(() => setSuccessMessage(""), 10000); // Сообщение исчезнет через 10 секунд
                // Сброс формы после бронирования
                setUsername("");
                setPassword("");
                setIsLoggedIn(true);
                // fetchUserBookings();
            } else {
                alert("Произошла ошибка при авторизации под записью админа, вы ввели некорректные данные");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при авторизации под записью админа");
        }
    }



    return (
    <div>
        <div className="big-box" id={"thank-you-title"}>
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
            </div>
        ) : (
                <div></div>
            )}
        <Link to={'/'}>
            <button>Перейти на главную</button>
        </Link>
    </div>
    )
}