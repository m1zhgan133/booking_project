from sqlalchemy import create_engine, Column, Integer, SmallInteger, Time, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import and_, or_, not_
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)

    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, index=True)
    id_place = Column(SmallInteger, nullable=False)
    id_user = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    st_datetime = Column(DateTime, nullable=False)
    en_datetime = Column(DateTime, nullable=False)
    duration = Column(Integer)

    user = relationship("User", back_populates="bookings")


# Создание таблиц (если они еще не существуют)
Base.metadata.create_all(bind=engine)


# ---------------------- Основные функции ----------------------

# ---------------------- CRUD для USERS
def create_user(name, password):
    session = SessionLocal()
    new_user = User(name=name, password=password)
    session.add(new_user)
    session.commit()
    session.close()


def get_user(name=None, password=None, id=None):
    session = SessionLocal()
    try:
        if not (name or password or id):
            return None

        # добавляем все фильтры не равные None
        filters = []
        if name:
            filters.append(User.name == name)
        if password:
            filters.append(User.password == password)
        if id:
            filters.append(User.id == id)
        user = session.query(User).filter(*filters).first()
        if not user: return None

        if user.bookings:
            user_bookings = []
            for booking in user.bookings:
                user_bookings.append({
                    "id": booking.id,
                    "id_place": booking.id_place,
                    "st_datetime": booking.st_datetime.isoformat(timespec='minutes'),
                    "en_datetime": booking.en_datetime.isoformat(timespec='minutes'),
                    "duration": booking.duration
                })
        else:
            user_bookings = None

        return {
            "id": user.id,
            "name": user.name,
            # "password": user.password, не будем так делать пожалуй ;)
            "bookings": user_bookings
        }
    finally:
        session.close()


def get_all_users():
    session = SessionLocal()
    users = session.query(User).all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "name": user.name,
            # "password": user.password
        })
    session.close()
    return users_list


def update_user(id, update_dict):
    session = SessionLocal()
    user = session.query(User).filter(User.id == id).first()
    if user:
        if update_dict['name']:
            user.name = update_dict['name']
        if update_dict['password']:
            user.password = update_dict['password']
        session.commit()
        session.close()
        return True
    session.close()
    return False


def delete_user(id):
    session = SessionLocal()
    user = session.query(User).filter(User.id == id).first()
    if not user:
        session.close()
        return False

    if user:
        session.delete(user)
        session.commit()
        session.close()
        return True


# ---------------------- CRUD для BOOKING
def create_booking(id_user, id_place, datetime_str, duration_minutes=120):
    session = SessionLocal()
    try:
        st_datetime = datetime.fromisoformat(datetime_str)
        en_datetime = st_datetime + timedelta(minutes=duration_minutes)

        new_booking = Booking(
            id_user=id_user,
            id_place=id_place,
            st_datetime=st_datetime,
            en_datetime=en_datetime,
            duration=duration_minutes
        )

        session.add(new_booking)
        session.commit()
        return new_booking
    except:
        return None
    finally:
        session.close()



def get_bookings_by_datetime_range(start_str, end_str):
    session = SessionLocal()

    start = datetime.fromisoformat(start_str)
    end = datetime.fromisoformat(end_str)

    bookings = session.query(Booking).filter(
        and_(
            not_(and_(Booking.st_datetime < start, Booking.en_datetime < start)),
            not_(and_(Booking.st_datetime > end, Booking.en_datetime > end))
        )
    ).all() # берет только тех у кого хоть какая-то часть лежит внутри интервала
    session.close()

    return [{
        "id": b.id,
        "id_user": b.id_user,
        "id_place": b.id_place,
        "st_datetime": b.st_datetime.isoformat(),
        "en_datetime": b.en_datetime.isoformat(),
        "duration": b.duration
    } for b in bookings]


def get_booking_by_id(booking_id):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    session.close()
    if booking:
        return {
            "id": booking.id,
            "id_place": booking.id_place,
            "id_user": booking.id_user,
            "st_datetime": booking.st_datetime.isoformat(timespec='minutes'),
            "en_datetime": booking.en_datetime.isoformat(timespec='minutes'),
            "duration": booking.duration,
            "user": {
                "id": booking.user.id,
                "name": booking.user.name
            } if booking.user else None
        }
    return None


def get_all_bookings():
    session = SessionLocal()
    try:
        bookings = session.query(Booking).all()
        return [{
            "id": b.id,
            "id_place": b.id_place,
            "id_user": b.id_user,
            "st_datetime": b.st_datetime.isoformat(timespec='minutes'),
            "en_datetime": b.en_datetime.isoformat(timespec='minutes'),
            "duration": b.duration
        } for b in bookings]
    finally:
        session.close()


def get_user_bookings(user_id):
    session = SessionLocal()
    bookings = session.query(Booking).filter(
        Booking.id_user == user_id
    ).order_by(Booking.st_datetime).all()
    session.close()

    return [{
        "id": b.id,
        "id_place": b.id_place,
        "id_user": b.id_user,
        "st_datetime": b.st_datetime.isoformat(timespec='minutes'),
        "en_datetime": b.en_datetime.isoformat(timespec='minutes'),
        "duration_minutes": b.duration
    } for b in bookings]


def update_booking(booking_id, data):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return False

    if 'id_place' in data:
        booking.id_place = data['id_place']

    if 'st_datetime' in data:
        new_st = datetime.fromisoformat(data['st_datetime'])
        booking.st_datetime = new_st
        booking.en_datetime = new_st + timedelta(minutes=booking.duration)

    if 'duration' in data:
        booking.duration = data['duration']
        booking.en_datetime = booking.st_datetime + timedelta(minutes=data['duration'])

    session.commit()
    session.close()
    return True

def delete_booking_by_id(booking_id):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        session.close()
        return False
    session.delete(booking)
    session.commit()
    session.close()
    return True

