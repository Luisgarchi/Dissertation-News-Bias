from opennews import scheduler


SCHEDULE_TIME = '0-20,40'

@scheduler.task(id = 'job1', trigger = 'cron', minute = SCHEDULE_TIME)
def myjob():
    print("Running Job")


