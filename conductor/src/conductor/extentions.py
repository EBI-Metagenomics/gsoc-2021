"""Conductor extensions."""


from celery import Celery

from conductor import global_config


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_engine = create_engine(global_config.get_sql_db_uri())
# Use this session for all db operations in the app
DBSession = sessionmaker(db_engine)

celery_app = Celery(
    __name__,
    broker=global_config.CELERY_BROKER_URL,
    backend=global_config.CELERY_RESULT_BACKEND,
)
