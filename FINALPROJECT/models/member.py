from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Member(Base):
    __tablename__ = "member"

    # primary key and attributes
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    goal_weight = Column(Numeric(5, 2))
    current_weight = Column(Numeric(5,  2))
    gender = Column(String(20), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    phone_number = Column(String(20), unique=True)
    email = Column(String(255), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint(
            "goal_weight IS NULL OR goal_weight > 0",
            name="ck_member_goal_weight_positive",
        ),
        CheckConstraint(
            "current_weight IS NULL OR current_weight > 0",
            name="ck_member_current_weight_positive",
        ),
        CheckConstraint(
            "gender IN ('Male','Female','Other','Prefer not to say')",
            name="ck_member_gender",
        ),
    )

    # member has one-to-many relationship to Session
    sessions = relationship("Session", back_populates="member")

    def __repr__(self) -> str:
        return f"<Member id={self.member_id} name={self.first_name} {self.last_name}>"

