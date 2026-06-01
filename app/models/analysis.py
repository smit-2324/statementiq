from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON, func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    bank_name = Column(String, default="")
    account_holder = Column(String, default="")
    statement_period = Column(String, default="")

    avg_monthly_deposits = Column(Float, default=0)
    avg_monthly_withdrawals = Column(Float, default=0)
    avg_daily_balance = Column(Float, default=0)
    ending_balance = Column(Float, default=0)
    lowest_balance = Column(Float, default=0)

    nsf_count = Column(Integer, default=0)
    overdraft_count = Column(Integer, default=0)
    mca_detected = Column(Boolean, default=False)

    result_json = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)

    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
