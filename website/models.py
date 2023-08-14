from flask_login import UserMixin
from datetime import datetime, timedelta
from. import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    slots = db.relationship('Slot', backref='user', lazy=True)

class Slot(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, start_time, end_time, user_id=None):
        self.start_time = start_time
        self.end_time = end_time
        self.is_booked = False
        self.user_id = user_id

    def is_slot_booked(self, selected_day):
        return Booking.query.filter(
            Booking.slot_id == self.id,
            Booking.timestamp >= selected_day.replace(hour=self.start_time.hour, minute=self.start_time.minute),
            Booking.timestamp < selected_day.replace(hour=self.end_time.hour, minute=self.end_time.minute)
        ).first() is not None

    def __repr__(self):
        return f"Slot {self.id} ({self.start_time} - {self.end_time})"
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"Booking {self.id} (User: {self.user_id}, Slot: {self.slot_id})"
    
    from website import db

class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

    # Add any other fields and relationships you need for your system model

    def __repr__(self):
        return f"System(id={self.id}, name={self.name}, is_booked={self.is_booked})"

