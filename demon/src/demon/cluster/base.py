"""Base cluster inteface."""

from abc import ABC, abstractmethod
from typing import List

from demon.schemas.job import Job


class BaseCluster(ABC):
    """Base cluster interface."""

    @abstractmethod
    def prepare_job(self: "BaseCluster", job: Job) -> None:
        """Prepare job for submission.

        Args:
            job (Job): Job object
        """

    @abstractmethod
    def submit_job(self: "BaseCluster", job: Job) -> str:
        """Submit job to the cluster.

        Args:
            job (Job): A Job object

        Returns:
            str: Job ID
        """
        pass

    @abstractmethod
    def get_job_status(self: "BaseCluster", job_id: str) -> List[str]:
        """Get status of a job by Job.

        Args:
            job_id (str): ID of the job

        Returns:
            List[str]: List of  status of the jobs # noqa DAR202
        """
        pass
