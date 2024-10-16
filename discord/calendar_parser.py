import requests
from datetime import datetime, timedelta
from dateutil.rrule import *
import pytz as tz
from icalendar import Calendar

localtz = tz.timezone('America/Toronto')

def cal_recurrences(recur_rule, start, exclusions, offset=0):
    now = localtz.localize(datetime.now()) + timedelta(days=offset)
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    dates = []
    for rule in rules.between(now.replace(hour=0, minute=0, second=0), now.replace(hour=23, minute=59, second=59)):
        dates.append(rule.timestamp())
    return dates

def get_events(calendar_url, offset=0):
    now = localtz.localize(datetime.now()) + timedelta(days=offset)
    events = []
    ical = requests.get(calendar_url)
    evcal = Calendar.from_ical(ical.content)
    for component in evcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            exdate = component.get('exdate')
            location = component.get('location') or "VRChat"

            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                for timestamp in cal_recurrences(reoccur, startdt, exdate, offset):
                    events.append((int(timestamp), str(summary), str(location)))
            else:
                if startdt > now.replace(hour=0, minute=0, second=0) and startdt < now.replace(hour=23, minute=59, second=59):
                    events.append(
                        (int(startdt.astimezone(localtz).timestamp()),
                         str(summary), str(location)))
    
    return sorted(events, key=lambda tup: tup[0]), (localtz.localize(datetime.now()) + timedelta(days=offset)).strftime('%A, %B %d')
