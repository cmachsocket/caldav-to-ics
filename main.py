import caldav
from icalendar import Calendar, Event
from dotenv import load_dotenv
import os
from ftplib import FTP

def create_folder_if_missing(folder_name):
    """
    Creates a folder if it doesn't exist
    :param folder_name: Folder name without leading or trailing slash
    :return: None
    """
    if not os.path.exists(f'{folder_name}/'):
        os.mkdir(f'{folder_name}/')


def export_calendar():
    export_cal = Calendar()
    export_cal.add('prodid', '-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN')
    export_cal.add('version', '2.0')

    # Use a breakpoint in the code line below to debug your script.
    client = caldav.DAVClient(os.getenv("CALDAV_URI"),
                              username=os.getenv("CALDAV_USR"),
                              password=os.getenv("CALDAV_PWD"))
    principal = client.principal()
    import_calendar = principal.calendars()[0]
    # NOTE: feishu CalDAV is partially broken in non-RFC ways:
    #   - calendar.calendars()[0].events()  → returns 0 (their
    #     calendar-query REPORT path is dead).
    #   - calendar.event_by_url(href).load() → GET on the .ics
    #     returns 403 Forbidden, so single-resource fetch is blocked.
    #   - sync-collection REPORT and calendar-multiget REPORT both
    #     work and return full VEVENT bodies. Use those.
    object_urls = [obj.url for obj in import_calendar.objects()]
    print(f'Found {len(object_urls)} calendar events.')
    # Multiget in batches of 20 — feishu handles small batches cleanly.
    BATCH = 20
    for i in range(0, len(object_urls), BATCH):
        batch = object_urls[i:i + BATCH]
        for import_event in import_calendar.calendar_multiget(batch):
            # feishu's multiget occasionally returns an empty body for
            # stale/deleted event hrefs still in sync-collection. Skip them.
            ical = import_event.icalendar_instance
            if ical is None:
                continue
            for subcomponent in ical.subcomponents:
                export_cal.add_component(subcomponent)

    create_folder_if_missing('out')
    f = open(os.path.join('out/calendar.ics'), 'wb')
    f.write(export_cal.to_ical())
    f.close()
    print(f'Exported calendar events.')
    pass


def upload_calendar_file():
    ftp = FTP(os.getenv('FTP_URI'))
    ftp.login(os.getenv('FTP_USR'), os.getenv('FTP_PWD'))
    print(f'Uploading to server...')
    with open('out/calendar.ics', 'rb') as f:
        ftp.storbinary(f'STOR {os.getenv("FTP_PATH")}', f)


if __name__ == '__main__':
    load_dotenv()
    export_calendar()
    # upload_calendar_file()

