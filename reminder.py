from apscheduler.schedulers.background import BackgroundScheduler
from icalendar import Calendar, Event
from desktop_notifier import DesktopNotifier, Urgency, Button
import datetime
import asyncio
PATH='out/calendar.ics'
def notification(summary):
    notifier = DesktopNotifier()
    asyncio.run(notifier.send(
        title="日程提醒",
        message=summary,
        urgency=Urgency.Critical  
    ))


def check_ics(path):
    global added_event
    with open(path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
        for component in cal.walk():
            if component.name == "VEVENT":
                uid = component.get('uid')
                if uid not in added_event:
                    print(f'New event added: {component.get("summary")} at {component.get("dtstart").dt}')
                    event_time = component.get('dtstart').dt
                    summary = component.get('SUMMARY')
                    scheduler.add_job(notification, 'date', run_date=event_time-datetime.timedelta(minutes=5), args=(summary,))
                    scheduler.add_job(notification, 'date', run_date=event_time-datetime.timedelta(minutes=15), args=(summary,))
                    scheduler.add_job(notification, 'date', run_date=event_time-datetime.timedelta(minutes=30), args=(summary,))
                    scheduler.add_job(notification, 'date', run_date=event_time-datetime.timedelta(minutes=60), args=(summary,))
                    added_event.add(uid)
    pass
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(check_ics, 'interval', minutes=5,args=(PATH))

added_event = set()

while True:
    pass