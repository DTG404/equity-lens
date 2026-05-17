"""Tests for APScheduler daemon integration."""

import pytest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytest import mark

from app.core.scheduler import start_scheduler, stop_scheduler


@pytest_asyncio.fixture
async def scheduler():
    sched = start_scheduler()
    yield sched
    stop_scheduler()


@mark.asyncio
async def test_scheduler_starts_and_has_jobs(scheduler: AsyncIOScheduler):
    assert scheduler is not None
    assert scheduler.running
    jobs = scheduler.get_jobs()
    assert len(jobs) >= 1


@mark.asyncio
async def test_scheduler_stop_cleans_up(scheduler: AsyncIOScheduler):
    stop_scheduler()
    # Calling stop again should be safe (idempotent)
    stop_scheduler()
