from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Session(Base):
    __tablename__ = "session"

    # primary key and attributes
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    session_type = Column(String(10), nullable=False)
    start_date_time = Column(DateTime, nullable=False)
    end_date_time = Column(DateTime, nullable=False)
    max_capacity = Column(Integer, nullable=False)

    # foreign keys
    room_id = Column(Integer, ForeignKey("room.room_id"), nullable=False)
    created_by_admin_id = Column(Integer, ForeignKey("admin_staff.admin_id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    member_id = Column(Integer, ForeignKey("member.member_id"))

    # session has many-to-one relationship to Room
    room = relationship("Room", back_populates="sessions")
    # session has many-to-one relationship to AdminStaff (as creator)
    created_by_admin = relationship("Admin_staff", back_populates="sessions_created")
    # session has many-to-one relationship to Trainer
    trainer = relationship("Trainer", back_populates="sessions")
    # session has many-to-one (optional) relationship to Member
    member = relationship("Member", back_populates="sessions")

    __table_args__ = (
        CheckConstraint(
            "session_type IN ('PT','CLASS')",
            name="ck_session_type",
        ),
        CheckConstraint(
            "max_capacity > 0",
            name="ck_session_max_capacity_positive",
        ),
        CheckConstraint(
            "end_date_time > start_date_time",
            name="ck_session_end_after_start",
        ),
    )

    def __repr__(self) -> str:
        return f"<Session id={self.session_id} type={self.session_type} start={self.start_date_time}>"