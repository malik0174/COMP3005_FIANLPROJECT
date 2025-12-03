# app/ddl_extras.py

from sqlalchemy import text
from database import engine


def create_view_index_trigger():
    """Create the VIEW, INDEX, and TRIGGER required by the project."""

    with engine.connect() as conn:
        # 1) VIEW: member dashboard showing upcoming sessions
        conn.execute(text("""
            CREATE OR REPLACE VIEW member_dashboard_view AS
            SELECT
                m.member_id,
                m.first_name,
                m.last_name,
                s.session_id,
                s.session_type,
                s.start_date_time,
                s.end_date_time,
                r.room_name,
                t.first_name AS trainer_first_name,
                t.last_name  AS trainer_last_name
            FROM member m
            JOIN session s   ON s.member_id = m.member_id
            JOIN room r      ON r.room_id = s.room_id
            JOIN trainer t   ON t.trainer_id = s.trainer_id
            WHERE s.start_date_time >= NOW()
            ORDER BY s.start_date_time;
        """))

        # 2) INDEX: help queries by room + start time
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session_room_start
            ON session (room_id, start_date_time);
        """))

        # 3) TRIGGER: prevent overlapping sessions in the same room
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION prevent_room_overlap()
            RETURNS trigger AS $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM session s
                    WHERE s.room_id = NEW.room_id
                      AND s.session_id <> COALESCE(NEW.session_id, -1)
                      AND NEW.start_date_time < s.end_date_time
                      AND NEW.end_date_time > s.start_date_time
                ) THEN
                    RAISE EXCEPTION 'Room is already booked for this time range';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))

        conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_prevent_room_overlap ON session;

            CREATE TRIGGER trg_prevent_room_overlap
            BEFORE INSERT OR UPDATE ON session
            FOR EACH ROW
            EXECUTE FUNCTION prevent_room_overlap();
        """))

        conn.commit()
        print("View, index, and trigger created.")
        

if __name__ == "__main__":
    create_view_index_trigger()