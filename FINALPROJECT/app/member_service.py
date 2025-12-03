"""
COMP3005 - Final Project: Health & Fitness Club Management System
File: member_service.py

Description:
This file contains helper functions that are focused on the "Member" role.
The goal is to separate out the higher-level logic (registering, updating profiles,
viewing dashboards, and booking PT sessions) from the lower-level ORM model code.

Author: Abdul Malik
"""

import os
import sys
from datetime import datetime

# Make sure the project root is on sys.path so that we can import `database` and `models`
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from database import get_session
from models.member import Member
from models.session import Session as SessionModel
from models.trainer import Trainer
from models.room import Room
from models.admin_staff import Admin_staff
from models.trainer_availability import TrainerAvailability  # for PT availability check


# This function is responsible for registering a brand new member.
# It takes basic information such as first name, last name, gender, email, phone number,
# plus some optional fitness details (date of birth and weights).
# If the email is already in use OR the gender is invalid, we return an error message instead.
def register_member(first_name: str,
                    last_name: str,
                    gender: str,
                    email: str,
                    phone_number: str | None = None,
                    dob_year: int | None = None,
                    dob_month: int | None = None,
                    dob_day: int | None = None,
                    goal_weight: float | None = None,
                    current_weight: float | None = None):
    """
    Create a new member row if the email (and phone, if provided) are not already in use.

    Returns:
        (member_id, error_message)
        - member_id: the newly created member_id (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    # clean up leading/trailing whitespace from the basic text fields
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()

    # CASE: if phone_number was provided, trim it as well
    if phone_number is not None:
        phone_number = phone_number.strip()
        # if the user only typed spaces, treat it as "no phone provided"
        if phone_number == "":
            phone_number = None

    # list of valid gender values (must match our CHECK constraint in the database)
    allowed_genders = ["Male", "Female", "Other", "Prefer not to say"]

    # CASE: user passes an invalid gender
    if gender not in allowed_genders:
        return None, f"Gender must be one of {allowed_genders}"

    # optional: basic DOB validation (only if the user tried to provide some values)
    if dob_year is not None or dob_month is not None or dob_day is not None:
        # if they start filling DOB, all three parts should be present
        if dob_year is None or dob_month is None or dob_day is None:
            return None, "If you provide date of birth, please include year, month, and day."

        # very light sanity checks (not a full calendar validator, which is fine for this project)
        if dob_year <= 0:
            return None, "Year of birth must be a positive integer."
        if not (1 <= dob_month <= 12):
            return None, "Month of birth must be between 1 and 12."
        if not (1 <= dob_day <= 31):
            return None, "Day of birth must be between 1 and 31."

    # optional: basic weight validation
    if goal_weight is not None and goal_weight <= 0:
        return None, "Goal weight must be a positive number."
    if current_weight is not None and current_weight <= 0:
        return None, "Current weight must be a positive number."

    # normal case: attempt to insert into the database
    with get_session() as db:
        # first check if someone with this email already exists
        existing_member = db.query(Member).filter_by(email=email).first()
        if existing_member is not None:
            return None, "A member with that email already exists."

        # optional: if a phone number was provided, make sure it is not already in use
        if phone_number is not None:
            existing_phone = (
                db.query(Member)
                .filter(Member.phone_number == phone_number)
                .first()
            )
            if existing_phone is not None:
                return None, "Another member already uses that phone number."

        # creating the new member object
        new_member = Member(
            goal_weight=goal_weight,
            current_weight=current_weight,
            gender=gender,
            first_name=first_name,
            last_name=last_name,
            year=dob_year,
            month=dob_month,
            day=dob_day,
            phone_number=phone_number,
            email=email,
        )

        # adding and flushing so that member_id is assigned
        db.add(new_member)
        db.flush()

        # IMPORTANT: grab the primitive id while the session is still open
        new_member_id = new_member.member_id

        return new_member_id, None


# This function lets an existing member update parts of their profile.
# For now we allow updating phone number and email address.
# We perform a couple of checks:
#   - The member_id must exist in the database.
#   - The new email (if provided) must not already belong to some other member.
def update_member_profile(member_id: int,
                          new_phone: str | None = None,
                          new_email: str | None = None):
    """
    Update a member's phone and/or email.

    Returns:
        (member, error_message)
        - member: the updated Member object (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    with get_session() as db:
        # look up the member we want to update
        member = db.query(Member).filter_by(member_id=member_id).first()

        # CASE: no such member exists
        if member is None:
            return None, f"Member with id {member_id} not found."

        # update the phone number if something non-empty was provided
        if new_phone is not None and new_phone.strip() != "":
            cleaned_phone = new_phone.strip()

            # optional: check if some OTHER member already has this phone number
            duplicate_phone = (
                db.query(Member)
                .filter(
                    Member.phone_number == cleaned_phone,
                    Member.member_id != member_id,
                )
                .first()
            )
            if duplicate_phone is not None:
                return None, "Another member already uses that phone number."

            member.phone_number = cleaned_phone

        # update the email address if something non-empty was provided
        if new_email is not None and new_email.strip() != "":
            cleaned_email = new_email.strip()

            # check if some OTHER member already has this email
            duplicate = (
                db.query(Member)
                .filter(
                    Member.email == cleaned_email,
                    Member.member_id != member_id,
                )
                .first()
            )
            if duplicate is not None:
                return None, "Another member already uses that email."

            member.email = cleaned_email

        # the context manager will commit changes automatically if no errors happen
        return member, None


# This function uses the member_dashboard_view we created earlier in ddl_extras.py.
# The idea is that the "dashboard" is just a convenient way of seeing all upcoming
# sessions for a given member: session type, start/end time, room, and trainer.
def get_member_dashboard(member_id: int) -> list[dict]:
    """
    Return a list of upcoming sessions for this member using member_dashboard_view.

    Each item in the returned list is a simple dictionary. This makes it easy
    to format and display inside a text-based menu / CLI.
    """

    with get_session() as db:
        # selecting only the columns we care about for display
        query_text = text(
            """
            SELECT
                session_id,
                session_type,
                start_date_time,
                end_date_time,
                room_name,
                trainer_first_name,
                trainer_last_name
            FROM member_dashboard_view
            WHERE member_id = :mid
            ORDER BY start_date_time;
            """
        )

        # executing the view with the specific member id
        result = db.execute(query_text, {"mid": member_id})

        # build the list of "dashboard rows" in one go
        dashboard_rows = [
            {
                "session_id": row.session_id,
                "session_type": row.session_type,
                "start": row.start_date_time,
                "end": row.end_date_time,
                "room_name": row.room_name,
                "trainer_name": f"{row.trainer_first_name} {row.trainer_last_name}",
            }
            for row in result
        ]

    return dashboard_rows


# This function is used when a member wants to book a personal training (PT) session.
# For now, to keep things manageable for the final project, we:
#   - Assume an admin is the one "creating" the session record (we can hard-code admin_id=1).
#   - Treat every PT session as having max_capacity = 1 by design.
#   - Rely on the database trigger to prevent overlapping bookings in the same room.
def schedule_pt_session(member_id: int,
                        trainer_id: int,
                        room_id: int,
                        start_dt: datetime,
                        end_dt: datetime,
                        created_by_admin_id: int = 1):
    """
    Create a PT session for a given member/trainer/room and time slot.

    Returns:
        (session, error_message)
        - session: the newly created Session object (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    # basic sanity check on times before hitting the database
    # CASE: user accidentally picks an end time that is before (or equal to) the start time
    if end_dt <= start_dt:
        return None, "End time must be after start time."

    # optional extra: PT sessions must start in the future
    if start_dt < datetime.now():
        return None, "You can't book a PT session in the past – please pick a future time."

    with get_session() as db:
        # look up all the referenced entities (foreign keys)
        member = db.query(Member).filter_by(member_id=member_id).first()
        trainer = db.query(Trainer).filter_by(trainer_id=trainer_id).first()
        room = db.query(Room).filter_by(room_id=room_id).first()
        admin = db.query(Admin_staff).filter_by(admin_id=created_by_admin_id).first()

        # series of checks to make sure everything exists
        if member is None:
            return None, f"Member with id {member_id} not found."
        if trainer is None:
            return None, f"Trainer with id {trainer_id} not found."
        if room is None:
            return None, f"Room with id {room_id} not found."
        if admin is None:
            return None, f"Admin_staff with id {created_by_admin_id} not found."

        # check that the trainer is actually available for this time range
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

        # prevent member double-booking across different rooms
        overlap_member = (
            db.query(SessionModel)
            .filter(
                SessionModel.member_id == member_id,
                SessionModel.start_date_time < end_dt,
                SessionModel.end_date_time > start_dt,
            )
            .first()
        )
        if overlap_member is not None:
            return None, "Member already has a session that overlaps this time."

        # prevent trainer double-booking across different rooms
        overlap_trainer = (
            db.query(SessionModel)
            .filter(
                SessionModel.trainer_id == trainer_id,
                SessionModel.start_date_time < end_dt,
                SessionModel.end_date_time > start_dt,
            )
            .first()
        )
        if overlap_trainer is not None:
            return None, "Trainer already has a session that overlaps this time."

        # constructing the new PT session
        new_session = SessionModel(
            session_type="PT",
            start_date_time=start_dt,
            end_date_time=end_dt,
            max_capacity=1,      # by definition, PT session is 1-on-1
            room=room,
            created_by_admin=admin,
            trainer=trainer,
            member=member,
        )

        db.add(new_session)

        try:
            # this is the moment where the trigger will fire and
            # complain if there is a room conflict
            db.flush()
        except Exception as e:
            # CASE: something went wrong (likely the trigger or another constraint)
            return None, f"Could not schedule session: {str(e)}"

        # normal case: everything worked
        return new_session, None