# app/seed_data.py

import os
import sys
from datetime import datetime, timedelta

# Ensure the project root (FINALPROJECT) is on sys.path so we can import `database` and `models`.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_session
from models.member import Member
from models.trainer import Trainer
from models.admin_staff import Admin_staff
from models.room import Room
from models.trainer_availability import TrainerAvailability
from models.session import Session as SessionModel  # avoid name clash with SQLAlchemy Session


def seed_data():
    """Insert sample admins, trainers, members, rooms, availabilities, and sessions."""

    with get_session() as db:
        # If we already have data, don't seed again
        if db.query(Admin_staff).first() is not None:
            print("Seed data already present; skipping.")
            return

        # --- Admin staff ---
        admin1 = Admin_staff(
            first_name="Inonu",
            last_name="Admin",
            phone_number="111-111-1111",
            email="inonu.admin@health.com",
        )
        admin2 = Admin_staff(
            first_name="Bob",
            last_name="Manager",
            phone_number="222-222-2222",
            email="bob.admin@health.com",
        )
        db.add_all([admin1, admin2])
        db.flush()  # assign IDs

        # --- Trainers ---
        trainer1 = Trainer(
            first_name="Johnny",
            last_name="Trainer",
            gender="Male",
            email="johnny.trainer@example.com",
        )
        trainer2 = Trainer(
            first_name="Amber",
            last_name="Coach",
            gender="Female",
            email="amber.trainer@example.com",
        )
        db.add_all([trainer1, trainer2])
        db.flush()

        # --- Members ---
        member1 = Member(
            first_name="Mia",
            last_name="Member",
            gender="Female",
            email="mia.member@example.com",
            phone_number="416-745-2847",
        )
        member2 = Member(
            first_name="Mike",
            last_name="Lifter",
            gender="Male",
            email="mike.lifter@example.com",
            phone_number="647-847-8577",
        )
        member3 = Member(
            first_name="Rachel",
            last_name="Cardio",
            gender="Other",
            email="rachel.cardio@example.com",
            phone_number="416-877-7777",
        )
        db.add_all([member1, member2, member3])
        db.flush()

        # --- Rooms ---
        room1 = Room(
            room_name="Weight Room",
            max_capacity=10,
            admin=admin1,  # managed by Inonu
        )
        room2 = Room(
            room_name="Cardio Studio",
            max_capacity=20,
            admin=admin2,  # managed by Bob
        )
        db.add_all([room1, room2])
        db.flush()

        # --- Trainer availability (tomorrow) ---
        now = datetime.now()
        day1 = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        t1_slot1_start = day1.replace(hour=9)
        t1_slot1_end   = day1.replace(hour=12)

        t2_slot1_start = day1.replace(hour=13)
        t2_slot1_end   = day1.replace(hour=17)

        avail1 = TrainerAvailability(
            trainer=trainer1,
            start_date_time=t1_slot1_start,
            end_date_time=t1_slot1_end,
        )
        avail2 = TrainerAvailability(
            trainer=trainer2,
            start_date_time=t2_slot1_start,
            end_date_time=t2_slot1_end,
        )
        db.add_all([avail1, avail2])
        db.flush()

        # --- Sessions (no overlapping times in same room) ---
        # PT session for Mia with Johnny in Weight Room
        pt1_start = day1.replace(hour=9)
        pt1_end   = day1.replace(hour=10)

        pt_session1 = SessionModel(
            session_type="PT",
            start_date_time=pt1_start,
            end_date_time=pt1_end,
            max_capacity=1,
            room=room1,
            created_by_admin=admin1,
            trainer=trainer1,
            member=member1,
        )

        # PT session for Mike with Johnny in Weight Room (back-to-back, non-overlapping)
        pt2_start = day1.replace(hour=10)
        pt2_end   = day1.replace(hour=11)

        pt_session2 = SessionModel(
            session_type="PT",
            start_date_time=pt2_start,
            end_date_time=pt2_end,
            max_capacity=1,
            room=room1,
            created_by_admin=admin1,
            trainer=trainer1,
            member=member2,
        )

        # CLASS session in Cardio Studio with Amber, no specific member
        class_start = day1.replace(hour=15)
        class_end   = day1.replace(hour=16)

        class_session = SessionModel(
            session_type="CLASS",
            start_date_time=class_start,
            end_date_time=class_end,
            max_capacity=15,
            room=room2,
            created_by_admin=admin2,
            trainer=trainer2,
            member=None,  # class has no single member
        )

        db.add_all([pt_session1, pt_session2, class_session])

        print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed_data()