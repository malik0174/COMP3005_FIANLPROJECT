from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    # primary key and attributes
    availability_id = Column(Integer, primary_key=True, autoincrement=True)
    start_date_time = Column(DateTime, nullable=False)
    end_date_time = Column(DateTime, nullable=False)
    # foreign key 
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)

    # trainer_availability has many-to-one relationship to Trainer
    trainer = relationship("Trainer", back_populates="availabilities")

    __table_args__ = (
        CheckConstraint(
            "end_date_time > start_date_time",
            name="ck_availability_end_after_start",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<TrainerAvailability id={self.availability_id} "
            f"trainer_id={self.trainer_id} start={self.start_date_time} end={self.end_date_time}>"
        )