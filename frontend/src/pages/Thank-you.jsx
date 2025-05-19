import React from "react";
import {Link} from "react-router-dom";

export default function ThankYou() {
    return (
        <div>
            <div className="big-box" id={"thank-you-title"}>
                <h2>Вы были успешно зарегестрированы!
                Спасибо что выбираете нас :)</h2>
            </div>
            <div className={"input-container"}>
                <img src="/images/kotik.jpg" alt="Здесь должен был быть котик" id={"cat-img"}/>
                <Link to={'/'}>
                    <button>Вернуться на главную</button>
                </Link>
            </div>
        </div>
    )
}