from datetime import datetime, timedelta, time
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, logging
from flask_login import login_required, current_user
from .models import Slot, Booking, System
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_week = today + timedelta(days=7)

    days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    return render_template("home.html", user=current_user, days=days, next_week=next_week)

time_slots = [
    (time(9, 0), time(11, 0)),
    (time(12, 0), time(14, 0)),
    (time(15, 0), time(17, 0)),
    (time(18, 0), time(20, 0))
]

@views.route('/slots/<selected_day>', methods=['GET'])
@login_required
def slots(selected_day):
    selected_date = datetime.strptime(selected_day, '%Y-%m-%d')
    selected_start = selected_date.replace(hour=9, minute=0)
    selected_end = selected_date.replace(hour=17, minute=0)

    available_slots = []

    for start_time, end_time in time_slots:
        slot = Slot.query.filter(
            Slot.start_time >= selected_start.replace(hour=start_time.hour, minute=start_time.minute),
            Slot.end_time <= selected_end.replace(hour=end_time.hour, minute=end_time.minute),
            Slot.is_booked == False
        ).first()
        if slot:
            available_slots.append(slot)

    return render_template("slots.html", user=current_user, selected_day=selected_date, available_slots=available_slots)

@views.route('/book-slot/<slot_id>', methods=['GET'])
@login_required
def book_slot(slot_id):
    slot = Slot.query.get(slot_id)

    if not slot:
        flash('Invalid slot selection.', category='error')
        return redirect(url_for('views.home'))

    if slot.is_booked:
        flash('Slot already booked.', category='error')
        return redirect(url_for('views.home'))

    # Store the booking details in the session for the payment page
    session['booking_slot_id'] = slot.id

    return redirect(url_for('views.payment'))

@views.route('/payment', methods=['GET'])
@login_required
def payment():
    selected_system = session.get('selected_system')

    if not selected_system:
        flash('No slot selected for booking.', category='error')
        return redirect(url_for('views.home'))

    slot = Slot.query.get(selected_system)
    return render_template("payment.html", user=current_user, slot=slot)

@views.route('/select-system/<slot_id>', methods=['GET', 'POST'])
@login_required
def select_system(slot_id):
    slot = Slot.query.get(slot_id)

    if not slot:
        flash('Invalid slot selection.', category='error')
        return redirect(url_for('views.home'))

    available_systems = System.query.all()

    if request.method == 'POST':
        selected_system = request.form.get('system')

        # Store the selected system in the session
        session['selected_system'] = selected_system

        # Redirect to the payment page
        return redirect(url_for('views.payment'))

    return render_template("select_system.html", user=current_user, slot=slot, available_systems=available_systems)

from sqlalchemy.exc import IntegrityError

@views.route('/confirm-booking', methods=['POST'])
@login_required
def confirm_booking():
    selected_system = session.get('selected_system')

    if not selected_system:
        flash('No system selected for booking.', category='error')
        return redirect(url_for('views.home'))

    # Find the system in the database based on the selected_system
    system = System.query.filter_by(name=selected_system).first()

    if not system:
        flash('Invalid system selection.', category='error')
        return redirect(url_for('views.home'))

    if system.is_booked:
        flash('System already booked.', category='error')
        return redirect(url_for('views.home'))

    # Mark the system as booked
    system.is_booked = True
    db.session.commit()

    # Create a booking record
    booking = Booking(user_id=current_user.id, system_id=system.id)
    db.session.add(booking)
    db.session.commit()

    # Clear the stored selected system from the session
    session.pop('selected_system', None)

    flash('Booking confirmed!', category='success')

    logging.info(f"Booking confirmed: User {current_user.id} booked {system.name}")

    return redirect(url_for('views.home'))
