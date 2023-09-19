from sqlalchemy import Column, BigInteger, String, sql, Float, Boolean

from utils.db_api.db_gino import TimedBaseModel


class User_data(TimedBaseModel):
    __tablename__ = 'user_data'
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(250))
    tg_last_name = Column(String(250))
    name = Column(String(100))
    email = Column(String(50))
    password = Column(String(50))
    number_machines = Column(String(250))
    name_machines = Column(String(250))
    sales = Column(String(10000))
    time_update = Column(BigInteger)
    report_time = Column(String(20))
    other_users = Column(String(250))
    status = Column(String(25))
    is_run = Column(Boolean)
    balance = Column(Float)
    bill_id = Column(String(200))

    query: sql.select
