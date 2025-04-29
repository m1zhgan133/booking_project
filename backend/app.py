from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/coworking'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    st_booking = db.Column(db.DateTime, nullable=False)
    en_booking = db.Column(db.DateTime, nullable=False)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

@app.route('/api/available', methods=['GET'])
def get_available():
    time_str = request.args.get('time')
    try:
        time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except:
        return jsonify({'error': 'Invalid time format'}), 400

    # Получаем занятые места
    booked = Booking.query.filter(
        Booking.st_booking <= time,
        Booking.en_booking > time
    ).all()

    booked_ids = [b.id for b in booked]
    all_ids = list(range(1, 21))
    available = [id for id in all_ids if id not in booked_ids]

    return jsonify({
        'booked': booked_ids,
        'available': available
    })


@app.route('/api/book', methods=['POST'])
def book_place():
    data = request.json
    # Добавьте валидацию данных
    new_booking = Booking(
        id=data['place_id'],
        user_id=data['user_id'],
        st_booking=datetime.strptime(data['st_booking'], '%Y-%m-%d %H:%M'),
        en_booking=datetime.strptime(data['en_booking'], '%Y-%m-%d %H:%M')
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)