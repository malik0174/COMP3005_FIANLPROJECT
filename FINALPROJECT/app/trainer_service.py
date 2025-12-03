"""
COMP3005 - Final Project: Health & Fitness Club Management System
File: trainer_service.py

Description:
This file contains helper functions that are focused on the "Trainer" role.
The idea is similar to member_service.py: keep the higher-level actions
(setting availability, viewing schedule) separate from the low-level ORM models.

Author: Abdul Malik
"""

import os
import sys
from datetime import datetime

# Make sure the project root is on sys.path so that we can import `database` and `models`
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_session
from models.trainer import Trainer
from models.trainer_availability import TrainerAvailability
from models.session import Session as SessionModel
from models.room import Room
from models.member import Member


# This function lets a trainer define a new availability window.
# We expect the CLI to parse the dates into datetime objects and pass them in.
# For now we keep the logic simple:
#   - End time must be after start time.
#   - Trainer must exist in the database.
def set_trainer_availability(trainer_id: int,
                             start_dt: datetime,
                             end_dt: datetime):
    """
    Create a new TrainerAvailability row for a given trainer and time window.

    Returns:
        (availability, error_message)
        - availability: the newly created TrainerAvailability object (or None if there was an error)
        - error_message: a string describing what went wrong (or None on success)
    """

    # quick sanity check on times before hitting the database
    if end_dt <= start_dt:
        return None, "End time must be after start time."

    # do not allow availability blocks that start in the past
    if start_dt < datetime.now():
        return None, "Availability must start in the future."

    with get_session() as db:
        # look up the trainer we are adding availability for
        trainer = db.query(Trainer).filter_by(trainer_id=trainer_id).first()

        # CASE: no such trainer
        if trainer is None:
            return None, f"Trainer with id {trainer_id} not found."

        # check for overlapping availability for this trainer
        # condition for overlap:
        #   existing.start < new_end AND existing.end > new_start
        overlapping = (
            db.query(TrainerAvailability)
            .filter(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.start_date_time < end_dt,
                TrainerAvailability.end_date_time > start_dt,
            )
            .first()
        )

        if overlapping is not None:
            return None, (
                "This availability conflicts with an existing availability window "
                f"({overlapping.start_date_time} -> {overlapping.end_date_time})."
            )

        # construct the availability row
        new_availability = TrainerAvailability(
            trainer=trainer,
            start_date_time=start_dt,
            end_date_time=end_dt,
        )

        db.add(new_availability)

        try:
            # this is where any CHECK constraints would fire
            db.flush()
        except Exception as e:
            # CASE: something went wrong (constraint, etc.)
            return None, f"Could not set availability: {str(e)}"

        # normal case: everything worked
        return new_availability, None


# This function returns all upcoming sessions for a given trainer.
# We use the Session ORM model and rely on relationships to pull room and member info.
def get_trainer_schedule(trainer_id: int) -> list[dict]:
    """
    Return a list of upcoming sessions for this trainer.

    Each item in the returned list is a simple dictionary with:
        - session_id
        - session_type
        - start
        - end
        - room_name
        - member_name (or a label if this is a CLASS with no single member)
    """

    schedule_rows: list[dict] = []
    now = datetime.now()

    with get_session() as db:
        # grab all future sessions for this trainer, ordered by start time
        sessions = (
            db.query(SessionModel)
            .filter(
                SessionModel.trainer_id == trainer_id,
                SessionModel.start_date_time >= now,
            )
            .order_by(SessionModel.start_date_time)
            .all()
        )

        # build a list of dictionaries suitable for printing in the CLI
        for sess in sessions:
            # room should be available via the relationship; we guard against None just in case
            room_name = sess.room.room_name if sess.room is not None else "Unknown room"

            # if this is a PT session, there should be a single member attached
            if sess.member is not None:
                member_name = f"{sess.member.first_name} {sess.member.last_name}"
            else:
                # CLASS session or something with no single member
                member_name = "(no single member)"

            row_dict = {
                "session_id": sess.session_id,
                "session_type": sess.session_type,
                "start": sess.start_date_time,
                "end": sess.end_date_time,
                "room_name": room_name,
                "member_name": member_name,
            }
            schedule_rows.append(row_dict)

    return schedule_rows