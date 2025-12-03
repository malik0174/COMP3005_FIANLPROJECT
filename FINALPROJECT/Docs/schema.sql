CREATE TABLE member (
    member_id       INTEGER GENERATED ALWAYS AS IDENTITY
                        (START WITH 1000 INCREMENT BY 1)
                        PRIMARY KEY, 
    goal_weight     NUMERIC(5,2) CHECK (goal_weight > 0),
    current_weight  NUMERIC(5,2) CHECK (current_weight > 0),
    gender          VARCHAR(10), CHECK (gender IN ('Male','Female','Other')),
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    year            INTEGER CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    month           INTEGER CHECK (month BETWEEN 1 AND 12),
    day             INTEGER,
    -- Make sure day is valid for the given month
    CHECK (
        day BETWEEN 1 AND
        CASE
            WHEN month IN (1, 3, 5, 7, 8, 10, 12) THEN 31
            WHEN month IN (4, 6, 9, 11)          THEN 30
            WHEN month = 2                       THEN 29   -- design choice to allow February 29 every year assumption
        END
    ),
    phone_number    VARCHAR(20) UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE trainer (
    trainer_id      INTEGER GENERATED ALWAYS AS IDENTITY
                        (START WITH 100 INCREMENT BY 1) 
                        PRIMARY KEY,
    gender          VARCHAR(10),
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    year            INTEGER CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    month           INTEGER CHECK (month BETWEEN 1 AND 12),
    day             INTEGER,
    -- Make sure day is valid for the given month
    CHECK (
        day BETWEEN 1 AND
        CASE
            WHEN month IN (1, 3, 5, 7, 8, 10, 12) THEN 31
            WHEN month IN (4, 6, 9, 11)          THEN 30
            WHEN month = 2                       THEN 29   -- design choice to allow February 29 every year assumption
        END
    ),
    email           VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE admin_staff (
    admin_id      INTEGER GENERATED ALWAYS AS IDENTITY 
                    (START WITH 1 INCREMENT BY 1)
                    PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    phone_number  VARCHAR(20),
    email         VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE room (
    room_id       INTEGER GENERATED ALWAYS AS IDENTITY 
                    (START WITH 10 INCREMENT BY 1)
                    PRIMARY KEY, 
    room_name     VARCHAR(100) NOT NULL,
    max_capacity  INTEGER NOT NULL CHECK (max_capacity > 0),
    admin_id      INTEGER NOT NULL REFERENCES admin_staff(admin_id)
                  ON DELETE RESTRICT
);

CREATE TABLE trainer_availability (
    availability_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_date_time  TIMESTAMP NOT NULL,
    end_date_time    TIMESTAMP NOT NULL,
    trainer_id       INTEGER NOT NULL REFERENCES trainer(trainer_id)
        ON DELETE CASCADE,
    CHECK (end_date_time > start_date_time)
);

CREATE TABLE session (
    session_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_type        VARCHAR(10) NOT NULL
        CHECK (session_type IN ('PT','CLASS')),
    start_date_time     TIMESTAMP NOT NULL,
    end_date_time       TIMESTAMP NOT NULL,
    max_capacity        INTEGER NOT NULL CHECK (max_capacity > 0),
    room_id             INTEGER NOT NULL REFERENCES room(room_id)
        ON DELETE RESTRICT,
    created_by_admin_id INTEGER NOT NULL REFERENCES admin_staff(admin_id)
        ON DELETE RESTRICT,
    trainer_id          INTEGER NOT NULL REFERENCES trainer(trainer_id)
        ON DELETE RESTRICT,
    member_id           INTEGER REFERENCES member(member_id)
        ON DELETE SET NULL,
    CHECK (end_date_time > start_date_time)
);