from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship 
from database import Base

class Room(Base):
    __tablename__ = "room"

    # primary key and attributes
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(100), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    # foriegn key
    admin_id = Column(Integer, ForeignKey("admin_staff.admin_id"), nullable=False)

    # room has many-to-one relationship to AdminStaff
    admin = relationship("Admin_staff", back_populates="rooms")
    # room has one-to-many relationship to Session
    sessions = relationship("Session", back_populates="room")

    __table_args__ = (
        CheckConstraint("max_capacity > 0", name="ck_room_max_capacity_positive"),
    )

    def __repr__(self) -> str:
        return f"<Room id={self.room_id} name={self.room_name}>"