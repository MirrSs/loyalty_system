from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .tasks.task_check_customer_linked_to_rcrm import task_check_customer_active


scheduler = AsyncIOScheduler()
cron_trigger_check_customer_linked_to_rcrm = CronTrigger(hour=3)

scheduler.add_job(
    task_check_customer_active,
    trigger=cron_trigger_check_customer_linked_to_rcrm,
)
