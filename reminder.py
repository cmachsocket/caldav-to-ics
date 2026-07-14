from apscheduler.schedulers.background import BackgroundScheduler
from icalendar import Calendar, Event
from desktop_notifier import DesktopNotifier, Urgency, Button
import datetime
import asyncio
import signal
ICS_PATH = 'out/calendar.ics'
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
scheduler.add_job(check_ics, 'interval', minutes=5, args=(ICS_PATH,))

added_event = set()

_stop = False


def _handle_signal(signum, _frame):
    global _stop
    _stop = True


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

# signal.pause() 在收到 signal 时被 EINTR 唤醒,直接返回。
# 比 threading.Event.wait() 靠谱 —— 后者遇到 EINTR 会自动重试,永远不退出。
while not _stop:
    signal.pause()

scheduler.shutdown(wait=False)