from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.database import Base

class DBGPTResult(Base):
    __tablename__ = "gpt_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
