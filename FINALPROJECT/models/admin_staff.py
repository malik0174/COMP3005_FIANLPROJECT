from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class Admin_staff(Base):
    __tablename__ = "admin_staff"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(255), nullable=False, unique=True)

    # admin_staff has one-to-many relationship to Room
    rooms = relationship("Room", back_populates="admin")
    # admin_staff has one-to-many relationship to Session (as creator)
    sessions_created = relationship("Session", back_populates="created_by_admin")

    def __repr__(self) -> str:
        return f"<Admin_staff id={self.admin_id} name={self.first_name} {self.last_name}>"