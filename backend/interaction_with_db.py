from sqlalchemy import create_engine, Column, Integer, SmallInteger, Time, String
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from dotenv import load_dotenv
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
    st_time = Column(Time, nullable=False)
    en_time = Column(Time, nullable=False)

    user = relationship("User", back_populates="bookings")


# Создание таблиц (если они еще не существуют)
Base.metadata.create_all(bind=engine)


# ---------------------- Основные функции ----------------------

# ---------------------- CRUD для USERS
def find_user(name=None, password=None):
    session = SessionLocal()
    user = None
    if name and password:
        user = session.query(User).filter(User.name == name,
                                          User.password == password).first()
    elif name:
        user = session.query(User).filter(User.name == name).first()
    elif password:
        user = session.query(User).filter(User.password == password).first()

    session.close()
    return user


def create_user(name, password):
    session = SessionLocal()
    new_user = User(name=name, password=password)
    session.add(new_user)
    session.commit()
    session.close()


def get_all_users():
    session = SessionLocal()
    users = session.query(User).all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "name": user.name,
            "password": user.password
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
    if user:
        session.delete(user)
        session.commit()
        session.close()
        return True
    session.close()
    return False

# ---------------------- CRUD для BOOKING
def create_booking(id_user, id_place, st_time, en_time):
    session = SessionLocal()
    new_booking = Booking(
        id_user=id_user,
        id_place=id_place,
        st_time=st_time,
        en_time=en_time
    )
    session.add(new_booking)
    session.commit()
    session.close()
    return new_booking

def get_booking(booking_id):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    session.close()
    if booking:
        return {
            "id": booking.id,
            "id_place": booking.id_place,
            "id_user": booking.id_user,
            "st_time": booking.st_time.strftime("%H:%M"),
            "en_time": booking.en_time.strftime("%H:%M")
        }
    return None

def get_all_bookings():
    session = SessionLocal()
    bookings = session.query(Booking).all()
    session.close()
    return [{
        "id": b.id,
        "id_place": b.id_place,
        "id_user": b.id_user,
        "st_time": b.st_time.strftime("%H:%M"),
        "en_time": b.en_time.strftime("%H:%M")
    } for b in bookings]

def get_user_bookings(user_id):
    session = SessionLocal()
    bookings = session.query(Booking).filter(Booking.id_user == user_id).all()
    session.close()
    return [{
        "id": b.id,
        "id_place": b.id_place,
        "st_time": b.st_time.strftime("%H:%M"),
        "en_time": b.en_time.strftime("%H:%M")
    } for b in bookings]

def update_booking(booking_id, update_data):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        if 'id_place' in update_data:
            booking.id_place = update_data['id_place']
        if 'st_time' in update_data:
            booking.st_time = update_data['st_time']
        if 'en_time' in update_data:
            booking.en_time = update_data['en_time']
        session.commit()
    session.close()
    return bool(booking)

def delete_booking(booking_id):
    session = SessionLocal()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        session.delete(booking)
        session.commit()
    session.close()
    return bool(booking)