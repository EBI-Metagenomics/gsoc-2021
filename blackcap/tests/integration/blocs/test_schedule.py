"""Schedule BloCs integration tests."""
# flake8: noqa

from typing import Dict

from blackcap.blocs.schedule import (
    create_schedule,
    delete_schedule,
    get_schedule,
    update_schedule,
)
from blackcap.configs import config_registry
from blackcap.scheduler import scheduler_registry
from blackcap.models.schedule import ScheduleDB
from blackcap.schemas.api.schedule.delete import ScheduleDelete
from blackcap.schemas.api.schedule.get import ScheduleGetQueryParams, ScheduleQueryType
from blackcap.schemas.api.schedule.post import ScheduleCreate
from blackcap.schemas.api.schedule.put import ScheduleUpdate
from blackcap.schemas.cluster import Cluster
from blackcap.schemas.job import Job
from blackcap.schemas.schedule import Schedule
from blackcap.schemas.user import User

from logzero import logger

from sqlalchemy import select
from sqlalchemy.orm.session import Session


config = config_registry.get_config()
scheduler = scheduler_registry.get_scheduler(config.SCHEDULER)


def test_scheduler_schedule(user: User, job: Job, cluster: Cluster) -> None:
    schedule_create_request = ScheduleCreate(job_id=job.job_id)
    scheduled_schedule_create_request = scheduler.schedule(schedule_create_request)
    created_schedule = create_schedule([scheduled_schedule_create_request], user)[0]
    assert job.job_id == created_schedule.job_id
