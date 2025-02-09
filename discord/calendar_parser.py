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
    
    # Convert exclusions to a list of datetime objects
    exclusion_dates = []
    if exclusions:
        if not isinstance(exclusions, list):
            exclusions = [exclusions]
        for xdate in exclusions:
            if hasattr(xdate, 'dts'):
                for dt in xdate.dts:
                    # Convert to timezone-aware datetime if it isn't already
                    ex_dt = dt.dt
                    if not isinstance(ex_dt, datetime):
                        ex_dt = datetime.combine(ex_dt, datetime.min.time())
                    if ex_dt.tzinfo is None:
                        ex_dt = localtz.localize(ex_dt)
                    exclusion_dates.append(ex_dt)
    
    # Add exclusion dates to the rule set
    dates_ex = []
    for ex_date in exclusion_dates:
        rules.exdate(ex_date)
        dates_ex.append(ex_date.date())
    
    dates = []
    day_start = now.replace(hour=0, minute=0, second=0)
    day_end = now.replace(hour=23, minute=59, second=59)
    
    for rule in rules.between(day_start, day_end):
        if rule.date() not in (dates_ex):
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
            
            # Handle timezone-naive datetime objects
            if isinstance(startdt, datetime) and startdt.tzinfo is None:
                startdt = localtz.localize(startdt)
            elif not isinstance(startdt, datetime):
                startdt = localtz.localize(datetime.combine(startdt, datetime.min.time()))
            
            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                for timestamp in cal_recurrences(reoccur, startdt, exdate, offset):
                    events.append((int(timestamp), str(summary), str(location)))
            else:
                day_start = now.replace(hour=0, minute=0, second=0)
                day_end = now.replace(hour=23, minute=59, second=59)
                if startdt > day_start and startdt < day_end:
                    events.append(
                        (int(startdt.astimezone(localtz).timestamp()),
                         str(summary), str(location)))
    
    return sorted(events, key=lambda tup: tup[0]), localtz.localize(datetime.now()) + timedelta(days=offset)
