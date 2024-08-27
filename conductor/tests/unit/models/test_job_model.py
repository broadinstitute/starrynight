"""Job model test suite."""

import pytest
from conductor.constants import JobType
from conductor.models.job import Job
from conductor.models.step import Step
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_create_job(db: Session, sample_step: Step) -> None:
    job = Job(
        name="TestJob",
        description="A test job",
        type=JobType.GEN_LOADDATA,
        outputs={},
        inputs={},
        step_id=sample_step.id,
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


def test_relationship_step(db: Session, sample_step: Step) -> None:
    job = Job(
        name="TestJob",
        description="A test job",
        type=JobType.GEN_LOADDATA,
        outputs={},
        inputs={},
        step_id=sample_step.id,
    )

    db.add(job)
    db.commit()
    db.refresh(sample_step)
    assert len(sample_step.jobs) == 1
    assert sample_step.jobs[0].id == job.id


def test_invalid_type(db: Session, sample_step: Step) -> None:
    with pytest.raises(IntegrityError, match="CHECK constraint failed"):
        job = Job(
            name="TestJob",
            description="A test job",
            type="InvalidType",
            outputs={},
            inputs={},
            step_id=sample_step.id,
        )
        db.add(job)
        db.commit()


def test_invalid_step(db: Session) -> None:
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        job = Job(
            name="TestJob",
            description="A test job",
            type=JobType.GEN_LOADDATA,
            outputs={},
            inputs={},
            step_id=2093482903,
        )
        db.add(job)
        db.commit()
