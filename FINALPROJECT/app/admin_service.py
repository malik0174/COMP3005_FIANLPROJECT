"""
COMP3005 - Final Project: Health & Fitness Club Management System
File: admin_service.py

Description:
This file contains helper functions that are focused on the "Admin_staff" role.
The idea is similar to member_service.py and trainer_service.py:
keep the higher-level actions (creating rooms and managing class sessions)
separate from the low-level ORM model classes.

Author: Abdul Malik
"""

import os
import sys
from datetime import datetime

# Make sure the project root is on sys.path so that we can import `database` and `models`
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_session
from models.admin_staff import Admin_staff
from models.trainer import Trainer
from models.room import Room
from models.trainer_availability import TrainerAvailability
from models.session import Session as SessionModel


# This function lets an admin create a brand new room in the gym.
# We keep the validation fairly small but reasonable:
#   - The admin_id must exist (Admin_staff row must be present).
#   - Room name cannot be an empty string.
#   - max_capacity must be a positive integer.
#   - Optionally: we prevent duplicate room names to keep things cleaner.
def create_room(admin_id: int,
                room_name: str,
                max_capacity: int):
    """
    Create a new Room row managed by the given admin.

    Returns:
        (room, error_message)
        - room: the newly created Room object (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    # basic cleanup and validation on the text / numeric inputs
    cleaned_name = room_name.strip()

    if cleaned_name == "":
        return None, "Room name cannot be empty."

    if max_capacity <= 0:
        return None, "Room capacity must be a positive integer."

    with get_session() as db:
        # look up the admin that will be responsible for this room
        admin = db.query(Admin_staff).filter_by(admin_id=admin_id).first()

        # CASE: no such admin found
        if admin is None:
            return None, f"Admin_staff with id {admin_id} not found."

        # optional: avoid duplicate room names (design choice)
        existing_room = (
            db.query(Room)
            .filter(Room.room_name == cleaned_name)
            .first()
        )
        if existing_room is not None:
            return None, "A room with that name already exists."

        # normal case: construct the Room row
        new_room = Room(
            room_name=cleaned_name,
            max_capacity=max_capacity,
            admin=admin,  # use the relationship
        )

        db.add(new_room)

        try:
            # let the database apply any CHECK constraints
            db.flush()
        except Exception as e:
            # CASE: some constraint or other DB issue fired
            return None, f"Could not create room: {str(e)}"

        # normal case: everything worked
        return new_room, None


# This function is used by the admin to create a CLASS session.
# Design choices for this project:
#   - session_type is always "CLASS" here.
#   - max_capacity is provided by the admin and must be > 0.
#   - The database trigger `prevent_room_overlap` will stop overlapping
#     sessions in the same room.
#   - We also check that the trainer is actually available for this
#     entire time window (using TrainerAvailability).
def create_class_session(admin_id: int,
                         trainer_id: int,
                         room_id: int,
                         start_dt: datetime,
                         end_dt: datetime,
                         max_capacity: int):
    """
    Create a CLASS session for a given trainer/room/time window.

    Returns:
        (session, error_message)
        - session: the newly created Session object (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    # quick sanity checks before touching the database
    if end_dt <= start_dt:
        return None, "End time must be after start time."

    if max_capacity <= 0:
        return None, "Class capacity must be a positive integer."

    # optional: disallow classes that start in the past
    if start_dt < datetime.now():
        return None, "Class must start in the future."

    with get_session() as db:
        # look up all the referenced entities (foreign keys)
        admin = db.query(Admin_staff).filter_by(admin_id=admin_id).first()
        trainer = db.query(Trainer).filter_by(trainer_id=trainer_id).first()
        room = db.query(Room).filter_by(room_id=room_id).first()

        # series of checks to make sure everything exists
        if admin is None:
            return None, f"Admin_staff with id {admin_id} not found."
        if trainer is None:
            return None, f"Trainer with id {trainer_id} not found."
        if room is None:
            return None, f"Room with id {room_id} not found."

        # NEW RULE: class capacity cannot exceed the room's capacity
        if max_capacity > room.max_capacity:
            return None, (
                f"Class capacity ({max_capacity}) cannot exceed room capacity "
                f"({room.max_capacity})."
            )

        # check that the trainer is actually available for this time range
        # here we require that the requested [start_dt, end_dt] is fully
        # contained inside at least one availability block.
        availability = (
            db.query(TrainerAvailability)
            .filter(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.start_date_time <= start_dt,
                TrainerAvailability.end_date_time >= end_dt,
            )
            .first()
        )

        if availability is None:
            return None, (
                "Trainer is not available for the requested time range. "
                "Please choose a window inside one of their availability blocks."
            )

        # NEW RULE: prevent the trainer from being double-booked
        trainer_conflict = (
            db.query(SessionModel)
            .filter(
                SessionModel.trainer_id == trainer_id,
                SessionModel.start_date_time < end_dt,
                SessionModel.end_date_time > start_dt,
            )
            .first()
        )

        if trainer_conflict is not None:
            return None, (
                "Trainer is already scheduled to teach another session "
                f"during this time window (session id {trainer_conflict.session_id})."
            )

        # construct the CLASS session; note member=None (it’s a group class)
        new_session = SessionModel(
            session_type="CLASS",
            start_date_time=start_dt,
            end_date_time=end_dt,
            max_capacity=max_capacity,
            room=room,
            created_by_admin=admin,
            trainer=trainer,
            member=None,  # CLASS sessions do not have a single member
        )

        db.add(new_session)

        try:
            # this is where the `prevent_room_overlap` trigger will fire
            # and block any conflicting sessions in the same room
            db.flush()
        except Exception as e:
            # CASE: overlapping room booking or some other constraint issue
            return None, f"Could not create class session: {str(e)}"

        # normal case: everything worked
        return new_session, None