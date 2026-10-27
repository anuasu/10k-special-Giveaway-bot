from datetime import time

from config import (
    TIMEZONE,
    BACKUP_HOUR,
    BACKUP_MINUTE,
)

from backup import scheduled_backup_job


def setup_scheduler(application):
    """
    Schedule the daily database backup at the configured India time.
    Call this function when setting up the Telegram application.
    """

    job_queue = application.job_queue

    if job_queue is None:
        raise RuntimeError(
            "JobQueue is unavailable. Install "
            "'python-telegram-bot[job-queue]' to enable scheduling."
        )

    # Prevent duplicate backup jobs if setup is called more than once.
    existing_jobs = job_queue.get_jobs_by_name("daily_database_backup")

    for job in existing_jobs:
        job.schedule_removal()

    backup_time = time(
        hour=BACKUP_HOUR,
        minute=BACKUP_MINUTE,
        second=0,
        tzinfo=TIMEZONE,
    )

    job_queue.run_daily(
        callback=scheduled_backup_job,
        time=backup_time,
        name="daily_database_backup",
    )

    print(
        f"✅ Daily database backup scheduled at "
        f"{BACKUP_HOUR:02d}:{BACKUP_MINUTE:02d} IST."
    )
