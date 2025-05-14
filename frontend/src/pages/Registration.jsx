import React, { useState } from 'react';
import {Link, useNavigate} from "react-router-dom";

export default function Registration() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errors, setErrors] = useState({});
    const navigate = useNavigate()

    const createUser = async () => {
        // проверяем все ли поля заполненны, если не заполненно подсвечиваем красным
        const newErrors = {
            username: !username,
            password: !password
        };

        // Проверяем, есть ли true
        const hasErrors = Object.values(newErrors).some(Boolean);
        if (hasErrors) {
            setErrors(newErrors);
            return;
        }
        setErrors({}); // Сброс ошибок

        try {
            const response = await fetch('/api/user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            if (response.status === 201) {
                setTimeout(() => navigate('/thank-you'), 100);
                // Сброс формы после бронирования
                setUsername("");
                setPassword("");
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Произошла ошибка при регистрации");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при регистрации");
        }
    };

    return (
        <div>
            <div className="big-box">
                <h2>Регистрация</h2>
            </div>
            <div className="input-container" id="registration-inputs-title">
                <label>Введите username</label>
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
                <button id="registration-button" onClick={createUser}>Зарегистрироваться</button>
            </div>
            <Link to={'/'}>
                <button id="back-home-button">Вернуться на главную</button>
            </Link>
        </div>
    );
}