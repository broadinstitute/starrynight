"""Job model test suite."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starrynight.modules.schema import Container

from conductor.models.job import Job
from conductor.models.project import Project


def test_create_job(db: Session, sample_project: Project) -> None:
    job = Job(
        name="TestJob",
        uid="module_id",
        description="A test job",
        outputs={},
        inputs={},
        spec={},
        project_id=sample_project.id,
    )
    db.add(job)
    db.commit()
    assert job.id is not None


# def test_unique_name(db: Session, sample_step: Step) -> None:
#     job1 = Job(
#         name="UniqueName",
#         description="A test job 1",
#         type=JobType.GEN_LOADDATA,
#         outputs={},
#         inputs={},
#         step_id=sample_step.id,
#     )
#     db.add(job1)
#     db.commit()
#
#     with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
#         job2 = Job(
#             name="UniqueName",
#             description="A test job 2",
#             type=JobType.GEN_LOADDATA,
#             outputs={},
#             inputs={},
#             step_id=sample_step.id,
#         )
#         db.add(job2)
#         db.commit()


def test_relationship_project(db: Session, sample_project: Project) -> None:
    job = Job(
        name="TestJob",
        uid="module_id",
        description="A test job",
        outputs={},
        inputs={},
        spec={},
        project_id=sample_project.id,
    )

    db.add(job)
    db.commit()
    db.refresh(sample_project)
    assert len(sample_project.jobs) == 1
    assert sample_project.jobs[0].id == job.id


def test_invalid_project(db: Session) -> None:
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        job = Job(
            name="TestJob",
            uid="module_id",
            description="A test job",
            outputs={},
            inputs={},
            spec={},
            project_id=2093482903,
        )
        db.add(job)
        db.commit()
