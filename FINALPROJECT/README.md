\# COMP3005 -- Final Project  
\## Health & Fitness Club Management System  
  
Author: Abdul Malik  
Course: COMP3005 -- Database Management Systems  
  
\-\--  
  
\## 1. Overview  
  
This project implements a small \*\*Health & Fitness Club Management
System\*\* using:  
  
- \*\*PostgreSQL\*\* for the relational database  
- \*\*SQLAlchemy ORM (Python)\*\* for the application layer  
- A simple \*\*text-based CLI\*\* with three roles:  
- Member  
- Trainer  
- Admin_staff (Admin)  
  
The idea is to show a reasonably normalized schema, some
constraints/triggers/views, and then a thin Python layer on top to demo
the core features.  
  
\-\--  
  
\## 2. Project structure  
  
From the root folder (\`FINALPROJECT/\`), the key files are:  
  
- \`database.py\`  
Sets up the SQLAlchemy engine and \`SessionLocal\` using a
\`DATABASE_URL\`.  
All the service files use \`get_session()\` from here.  
  
- \`schema.sql\`  
Original raw SQL schema I used while designing the database.  
The Python code does \*\*not\*\* depend on it anymore, but I kept it for
reference/marking.  
  
- \`app/\`  
- \`main.py\`  
Entry point for the CLI (Member / Trainer / Admin menus).  
- \`init_db.py\`  
Drops & recreates all tables using the SQLAlchemy ORM models.  
- \`ddl_extras.py\`  
Creates "extra" DB objects like:  
- \`member_dashboard_view\`  
- trigger + function to prevent overlapping sessions in the same room.  
- \`seed_data.py\`  
Populates the database with sample data:  
- admin staff, trainers, members, rooms, trainer availability, and some
sessions.  
- \`member_service.py\`  
Helper functions for the \*\*Member\*\* role  
(register, update profile, view dashboard, book PT sessions).  
- \`trainer_service.py\`  
Helper functions for the \*\*Trainer\*\* role  
(set availability, view upcoming sessions).  
- \`admin_service.py\`  
Helper functions for the \*\*Admin_staff\*\* role  
(create rooms, create CLASS sessions).  
- \`models/\`  
SQLAlchemy ORM models for all tables  
(\`Member\`, \`Trainer\`, \`Room\`, \`Session\`,
\`TrainerAvailability\`, \`Admin_staff\`, etc).  
- \`\_\_init\_\_.py\`  
Just marks \`app\` as a Python package.  
  
\-\--  
  
\## 3. Requirements  
  
- \*\*Python\*\* 3.10+  
- \*\*PostgreSQL\*\* (local instance; tested with a local DB)  
- Python packages:  
- \`sqlalchemy\`  
- \`psycopg2-binary\`  
  
Install the Python dependencies (from the project root):  
  
\`\`\`bash  
pip install sqlalchemy psycopg2-binary  
  
\## 4. Running Instructions  
  
python3 -m app.init_db  
python3 -m app.ddl_extras  
python3 -m app.seed_data  
  
Any time you want to reset the database back to the default seeded
state, just run init_db to drop and recreate all the tables, ddl_extras
to recreate my view and trigger, and then seed_data to populate the
database with the initial sample records.  
  
VIDEO LINK: https://youtu.be/W8Bn75ZclRw
