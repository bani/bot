import requests
from datetime import datetime
from dateutil.rrule import *
import pytz as tz
from icalendar import Calendar


localtz = tz.timezone('America/Toronto')
now = localtz.localize(datetime.now())
calendar_url = 'https://calendar.google.com/calendar/ical/mmi03hniu9rl24ej5thlb0o2stimvtq3%40import.calendar.google.com/public/basic.ics'

def cal_recurrences(recur_rule, start, exclusions):
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
    for rule in rules.between(now, now.replace(hour=23, minute=59, second=59)):
        dates.append(rule.timestamp())
    return dates

def get_events():
    events = []
    ical = requests.get(calendar_url)
    evcal = Calendar.from_ical(ical.content)
    for component in evcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            exdate = component.get('exdate')
            location = component.get('location')
            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                for item in cal_recurrences(reoccur, startdt, exdate):
                    events.append((int(item), str(summary)))
            else:
                if startdt > now and startdt < now.replace(hour=23, minute=59, second=59):
                    events.append(
                        (int(startdt.astimezone(localtz).timestamp()),
                         str(location),
                         str(summary)))
    
    return sorted(events, key=lambda tup: tup[0])

def get_nonrecurring():
    events = []
    ical = requests.get(calendar_url)
    evcal = Calendar.from_ical(ical.content)
    for component in evcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            if not component.get('rrule'):
                if startdt > now and startdt < now.replace(month=now.month+1):
                    events.append((int(startdt.astimezone(localtz).timestamp()), str(summary)))
    
    return sorted(events, key=lambda tup: tup[0])


events = get_events()
for e in events:
    print(f"<t:{e[0]}:t>: {e[2]} ({e[1]})")
