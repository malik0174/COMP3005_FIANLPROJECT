"""
COMP3005 - Final Project: Health & Fitness Club Management System
File: main.py

Description:
This file is the main entry point for the application. It provides a very simple,
text-based menu system that lets us "pretend" to be different roles
(Member / Trainer / Admin) and call the appropriate helper functions.
"""

import os
import sys
from datetime import datetime

# Make sure the project root is on sys.path (so we can import the app package properly)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.member_service import (
    register_member,
    update_member_profile,
    get_member_dashboard,
    schedule_pt_session,
)

from app.trainer_service import (
    set_trainer_availability,
    get_trainer_schedule,
)

from app.admin_service import (
    create_room,
    create_class_session,
)


# helper function that converts user input into a datetime object
# we expect input in the format "YYYY-MM-DD HH:MM"
def parse_datetime(prompt: str) -> datetime | None:
    """
    Ask the user for a datetime in 'YYYY-MM-DD HH:MM' format
    and return a datetime object (or None if the input was invalid).
    """
    raw_input = input(f"{prompt} (YYYY-MM-DD HH:MM): ").strip()

    try:
        return datetime.strptime(raw_input, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid datetime format. Please use 'YYYY-MM-DD HH:MM'.")
        return None


# This function represents the "Member" menu.
# It is called from the main loop and it keeps looping until the user decides
# to go back to the main menu.
def member_menu():
    while True:
        print("\n=== MEMBER MENU ===")
        print("1) Register new member")
        print("2) Update member profile")
        print("3) View member dashboard")
        print("4) Schedule PT session")
        print("0) Back to main menu")

        choice = input("Choose an option: ").strip()

        # OPTION 1: Register a new member
        if choice == "1":
            print("\n--- Register New Member ---")

            first_name = input("First name: ").strip()
            last_name = input("Last name: ").strip()
            gender = input("Gender (Male/Female/Other/Prefer not to say): ").strip()
            email = input("Email: ").strip()
            phone = input("Phone (optional): ").strip()

            # if the user leaves phone blank, treat it as None
            if phone == "":
                phone = None

            # date of birth fields (all optional, but if they start, they should complete them)
            dob_year_input = input("Year of birth (YYYY, optional): ").strip()
            dob_month_input = input("Month of birth (1-12, optional): ").strip()
            dob_day_input = input("Day of birth (1-31, optional): ").strip()

            dob_year = dob_month = dob_day = None

            # parse year if provided
            if dob_year_input != "":
                try:
                    dob_year = int(dob_year_input)
                except ValueError:
                    print("Year of birth must be a whole number (e.g., 1999).")
                    continue

            # parse month if provided
            if dob_month_input != "":
                try:
                    dob_month = int(dob_month_input)
                except ValueError:
                    print("Month of birth must be a whole number between 1 and 12.")
                    continue

            # parse day if provided
            if dob_day_input != "":
                try:
                    dob_day = int(dob_day_input)
                except ValueError:
                    print("Day of birth must be a whole number between 1 and 31.")
                    continue

            # fitness-related details (all optional)
            goal_weight_input = input("Goal weight (e.g., in kg, optional): ").strip()
            current_weight_input = input("Current weight (e.g., in kg, optional): ").strip()

            goal_weight = current_weight = None

            if goal_weight_input != "":
                try:
                    goal_weight = float(goal_weight_input)
                except ValueError:
                    print("Goal weight must be a number (you can use decimals).")
                    continue

            if current_weight_input != "":
                try:
                    current_weight = float(current_weight_input)
                except ValueError:
                    print("Current weight must be a number (you can use decimals).")
                    continue

            member_id, error = register_member(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                email=email,
                phone_number=phone,
                dob_year=dob_year,
                dob_month=dob_month,
                dob_day=dob_day,
                goal_weight=goal_weight,
                current_weight=current_weight,
            )

            if error is not None:
                print("Error:", error)
            else:
                print(f"Member created successfully with id = {member_id}")

        # OPTION 2: Update an existing member's profile
        elif choice == "2":
            member_id_input = input("Member ID to update: ").strip()

            # basic integer validation
            try:
                member_id = int(member_id_input)
            except ValueError:
                print("Invalid member id. Please enter a numeric value.")
                continue

            new_phone = input("New phone (leave blank to keep current): ").strip()
            new_email = input("New email (leave blank to keep current): ").strip()

            # convert empty strings to None so that the update function knows not to touch them
            if new_phone == "":
                new_phone = None
            if new_email == "":
                new_email = None

            member, error = update_member_profile(
                member_id,
                new_phone=new_phone,
                new_email=new_email,
            )

            if error is not None:
                print("Error:", error)
            else:
                print("Profile updated successfully:")
                print(f"- Name:  {member.first_name} {member.last_name}")
                print(f"- Phone: {member.phone_number}")
                print(f"- Email: {member.email}")

        # OPTION 3: View dashboard (upcoming sessions from the view)
        elif choice == "3":
            member_id_input = input("Member ID: ").strip()

            try:
                member_id = int(member_id_input)
            except ValueError:
                print("Invalid member id. Please enter a numeric value.")
                continue

            dashboard_rows = get_member_dashboard(member_id)

            # CASE: no upcoming sessions
            if len(dashboard_rows) == 0:
                print("No upcoming sessions for this member.")
            else:
                print(f"\nUpcoming sessions for member {member_id}:\n")

                # small ASCII-style table header
                print("+----------+----------+------------------+------------------+----------------------+----------------------+")
                print("| Session  | Type     | Start            | End              | Room                 | Trainer              |")
                print("+----------+----------+------------------+------------------+----------------------+----------------------+")

                # printing each session in a nice aligned row
                for row in dashboard_rows:
                    start_str = row["start"].strftime("%Y-%m-%d %H:%M")
                    end_str = row["end"].strftime("%Y-%m-%d %H:%M")

                    print(
                        "| "
                        f"{str(row['session_id']).ljust(8)} | "
                        f"{row['session_type'][:8].ljust(8)} | "
                        f"{start_str.ljust(16)} | "
                        f"{end_str.ljust(16)} | "
                        f"{row['room_name'][:20].ljust(20)} | "
                        f"{row['trainer_name'][:20].ljust(20)} |"
                    )

                print("+----------+----------+------------------+------------------+----------------------+----------------------+\n")

        # OPTION 4: Schedule a new PT session
        elif choice == "4":
            member_id_input = input("Member ID: ").strip()
            trainer_id_input = input("Trainer ID: ").strip()
            room_id_input = input("Room ID: ").strip()

            # converting ids to integers
            try:
                member_id = int(member_id_input)
                trainer_id = int(trainer_id_input)
                room_id = int(room_id_input)
            except ValueError:
                print("Member / trainer / room IDs must all be integers.")
                continue

            # gathering time information from the user
            start_dt = parse_datetime("Start datetime")
            if start_dt is None:
                continue

            end_dt = parse_datetime("End datetime")
            if end_dt is None:
                continue

            # quick sanity check that end time is after the start time
            if end_dt <= start_dt:
                print("End time must be after start time.")
                continue

            # For demo purposes, we assume admin with id 1 is doing the booking.
            session, error = schedule_pt_session(
                member_id=member_id,
                trainer_id=trainer_id,
                room_id=room_id,
                start_dt=start_dt,
                end_dt=end_dt,
                created_by_admin_id=1,
            )

            if error is not None:
                print("Error:", error)
            else:
                print(
                    f"PT session created with id = {session.session_id} "
                    f"from {session.start_date_time} to {session.end_date_time}"
                )

        # OPTION 0: go back to the main menu
        elif choice == "0":
            break

        # CASE: user picked something that is not a valid option
        else:
            print("Invalid choice. Please try again.")


# This function represents the "Trainer" menu.
# It is called from the main loop and it keeps looping until the trainer decides
# to go back to the main menu.
def trainer_menu():
    print("\n=== TRAINER MENU ===")
    trainer_id_input = input("Enter your trainer ID (e.g., 100): ").strip()

    # basic validation on trainer_id
    try:
        trainer_id = int(trainer_id_input)
    except ValueError:
        print("Invalid trainer id. Please enter a numeric value.")
        return

    while True:
        print("\n=== TRAINER MENU ===")
        print("1) Set availability")
        print("2) View my upcoming sessions")
        print("0) Back to main menu")

        choice = input("Choose an option: ").strip()

        # OPTION 1: Set availability window
        if choice == "1":
            print("\n--- Set Trainer Availability ---")
            start_dt = parse_datetime("Start datetime")
            if start_dt is None:
                continue

            end_dt = parse_datetime("End datetime")
            if end_dt is None:
                continue

            availability, error = set_trainer_availability(
                trainer_id=trainer_id,
                start_dt=start_dt,
                end_dt=end_dt,
            )

            if error is not None:
                print("Error:", error)
            else:
                print(
                    f"Availability created with id = {availability.availability_id} "
                    f"from {availability.start_date_time} to {availability.end_date_time}"
                )

        # OPTION 2: View all upcoming sessions for this trainer
        elif choice == "2":
            print("\n--- My Upcoming Sessions ---")
            schedule_rows = get_trainer_schedule(trainer_id)

            if len(schedule_rows) == 0:
                print("No upcoming sessions for this trainer.")
            else:
                print(f"\nUpcoming sessions for trainer {trainer_id}:\n")

                # ASCII-style table header for trainer schedule
                print("+----------+----------+------------------+------------------+----------------------+----------------------+")
                print("| Session  | Type     | Start            | End              | Room                 | Member               |")
                print("+----------+----------+------------------+------------------+----------------------+----------------------+")

                for row in schedule_rows:
                    # format datetimes nicely
                    start_str = row["start"].strftime("%Y-%m-%d %H:%M")
                    end_str = row["end"].strftime("%Y-%m-%d %H:%M")

                    print(
                        "| "
                        f"{str(row['session_id']).ljust(8)} | "
                        f"{row['session_type'][:8].ljust(8)} | "
                        f"{start_str.ljust(16)} | "
                        f"{end_str.ljust(16)} | "
                        f"{row['room_name'][:20].ljust(20)} | "
                        f"{row['member_name'][:20].ljust(20)} |"
                    )

                print("+----------+----------+------------------+------------------+----------------------+----------------------+\n")


        # OPTION 0: back to main menu
        elif choice == "0":
            break

        else:
            print("Invalid choice. Please try again.")


# This function represents the "Admin_staff" menu.
# It is called from the main loop and it keeps looping until the admin decides
# to go back to the main menu.
def admin_menu():
    print("\n=== ADMIN MENU ===")
    admin_id_input = input("Enter your admin ID (e.g., 1): ").strip()

    # basic validation on admin_id
    try:
        admin_id = int(admin_id_input)
    except ValueError:
        print("Invalid admin id. Please enter a numeric value.")
        return

    while True:
        print("\n=== ADMIN MENU ===")
        print("1) Create a new room")
        print("2) Create a new CLASS session")
        print("0) Back to main menu")

        choice = input("Choose an option: ").strip()

        # OPTION 1: Create a new room
        if choice == "1":
            print("\n--- Create Room ---")
            room_name = input("Room name: ").strip()
            max_capacity_input = input("Max capacity: ").strip()

            # capacity must be an integer
            try:
                max_capacity = int(max_capacity_input)
            except ValueError:
                print("Max capacity must be a positive integer.")
                continue

            room, error = create_room(
                admin_id=admin_id,
                room_name=room_name,
                max_capacity=max_capacity,
            )

            if error is not None:
                print("Error:", error)
            else:
                print(
                    f"Room created with id = {room.room_id} "
                    f"('{room.room_name}', capacity {room.max_capacity})"
                )

        # OPTION 2: Create a CLASS session
        elif choice == "2":
            print("\n--- Create CLASS Session ---")
            trainer_id_input = input("Trainer ID: ").strip()
            room_id_input = input("Room ID: ").strip()
            max_cap_input = input("Class max capacity: ").strip()

            # converting ids and capacity to integers
            try:
                trainer_id = int(trainer_id_input)
                room_id = int(room_id_input)
                max_capacity = int(max_cap_input)
            except ValueError:
                print("Trainer ID, Room ID, and capacity must all be integers.")
                continue

            # gathering time information from the user
            start_dt = parse_datetime("Start datetime")
            if start_dt is None:
                continue

            end_dt = parse_datetime("End datetime")
            if end_dt is None:
                continue

            # quick sanity check that end time is after the start time
            if end_dt <= start_dt:
                print("End time must be after start time.")
                continue

            session, error = create_class_session(
                admin_id=admin_id,
                trainer_id=trainer_id,
                room_id=room_id,
                start_dt=start_dt,
                end_dt=end_dt,
                max_capacity=max_capacity,
            )

            if error is not None:
                print("Error:", error)
            else:
                print(
                    f"CLASS session created with id = {session.session_id} "
                    f"from {session.start_date_time} to {session.end_date_time} "
                    f"in room {session.room.room_name} (capacity {session.max_capacity})"
                )

        # OPTION 0: back to main menu
        elif choice == "0":
            break

        else:
            print("Invalid choice. Please try again.")


# This is the main entry point for the whole application.
# It now exposes the Member, Trainer, and Admin menus.
def main():
    while True:
        print("\n=== HEALTH CLUB SYSTEM ===")
        print("1) Member role")
        print("2) Trainer role")
        print("3) Admin role")
        print("0) Exit")

        menu_choice = input("Choose an option: ").strip()

        if menu_choice == "1":
            member_menu()
        elif menu_choice == "2":
            trainer_menu()
        elif menu_choice == "3":
            admin_menu()
        elif menu_choice == "0":
            print("Exiting program. Goodbye.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()