from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from datetime import datetime
from app.database import Base

class DBResume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # You can later convert this to a ForeignKey
    file_id = Column(String, unique=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now())
    analysis_result = Column(JSON, nullable=True)
    review = Column(Text, nullable=True)
