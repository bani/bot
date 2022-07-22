import requests
from datetime import datetime
from dateutil.rrule import *
import pytz as tz
from icalendar import Calendar


localtz = tz.timezone('America/Toronto')
now = localtz.localize(datetime.now())

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
    ical = requests.get("https://calendar.google.com/calendar/ical/c_qc3lsjssl0f2mhrljmptf78430%40group.calendar.google.com/public/basic.ics")
    evcal = Calendar.from_ical(ical.content)
    for component in evcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            exdate = component.get('exdate')
            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                for item in cal_recurrences(reoccur, startdt, exdate):
                    events.append((int(item), str(summary)))
            else:
                if startdt > now and startdt < now.replace(hour=23, minute=59, second=59):
                    events.append((int(startdt.astimezone(localtz).timestamp()), str(summary)))
    
    return sorted(events, key=lambda tup: tup[0])

def get_nonrecurring():
    events = []
    ical = requests.get("https://calendar.google.com/calendar/ical/c_qc3lsjssl0f2mhrljmptf78430%40group.calendar.google.com/public/basic.ics")
    evcal = Calendar.from_ical(ical.content)
    for component in evcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            if not component.get('rrule'):
                if startdt > now and startdt < now.replace(month=now.month+1):
                    events.append((int(startdt.astimezone(localtz).timestamp()), str(summary)))
    
    return sorted(events, key=lambda tup: tup[0])