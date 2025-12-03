from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Trainer(Base):
    __tablename__ = "trainer"

    # primary key and attributes
    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    gender = Column(String(20))  
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    email = Column(String(255), nullable=False, unique=True)

    # trainer has one-to-many relationship to TrainerAvailability
    availabilities = relationship("TrainerAvailability", back_populates="trainer")
    # trainer has one-to-many relationship to Session
    sessions = relationship("Session", back_populates="trainer")

    __table_args__ = (
        CheckConstraint(
            "gender IN ('Male','Female','Other','Prefer not to say')",
            name="ck_trainer_gender",
        ),
    )

    def __repr__(self) -> str:
        return f"<Trainer id={self.trainer_id} name={self.first_name} {self.last_name}>"