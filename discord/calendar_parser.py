"""Fetch a single day's events from an iCal feed."""

from datetime import datetime, timedelta

import pytz
import requests
from dateutil.rrule import rrulestr, rruleset
from icalendar import Calendar

LOCALTZ = pytz.timezone('America/Toronto')
REQUEST_TIMEOUT = 30


def _day_bounds(day):
    """First and last microsecond of `day`, for use as rruleset.between
    bounds (between() excludes its endpoints)."""
    return (
        day.replace(hour=0, minute=0, second=0, microsecond=0),
        day.replace(hour=23, minute=59, second=59, microsecond=999999),
    )


def _exclusion_dates(exclusions):
    """Flatten an icalendar EXDATE property into timezone-aware datetimes."""
    if not exclusions:
        return []
    if not isinstance(exclusions, list):
        exclusions = [exclusions]

    dates = []
    for exdate in exclusions:
        for entry in getattr(exdate, 'dts', []):
            ex_dt = entry.dt
            if not isinstance(ex_dt, datetime):
                ex_dt = datetime.combine(ex_dt, datetime.min.time())
            if ex_dt.tzinfo is None:
                ex_dt = LOCALTZ.localize(ex_dt)
            dates.append(ex_dt)
    return dates


def cal_recurrences(recur_rule, start, exclusions, day_start, day_end):
    """Timestamps of a recurring event's occurrences between the day bounds."""
    rules = rruleset()
    rules.rrule(rrulestr(recur_rule, dtstart=start))

    excluded_days = set()
    for ex_dt in _exclusion_dates(exclusions):
        rules.exdate(ex_dt)
        excluded_days.add(ex_dt.date())

    return [
        occurrence.timestamp()
        for occurrence in rules.between(day_start, day_end)
        if occurrence.date() not in excluded_days
    ]


def get_events(calendar_url, offset=0):
    """Events on today+offset days, as sorted (timestamp, summary, location)
    tuples, along with the localized datetime of that day."""
    target_day = LOCALTZ.localize(datetime.now()) + timedelta(days=offset)
    day_start, day_end = _day_bounds(target_day)
    events = []

    response = requests.get(calendar_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        summary = component.get('summary')
        startdt = component.get('dtstart').dt
        location = component.get('location') or "VRChat"

        # All-day events come back as plain dates; normalize everything to
        # timezone-aware datetimes.
        if not isinstance(startdt, datetime):
            startdt = LOCALTZ.localize(datetime.combine(startdt, datetime.min.time()))
        elif startdt.tzinfo is None:
            startdt = LOCALTZ.localize(startdt)

        rrule = component.get('rrule')
        if rrule:
            recur_rule = rrule.to_ical().decode('utf-8')
            exclusions = component.get('exdate')
            for timestamp in cal_recurrences(recur_rule, startdt, exclusions,
                                             day_start, day_end):
                events.append((int(timestamp), str(summary), str(location)))
        elif day_start < startdt < day_end:
            events.append((int(startdt.astimezone(LOCALTZ).timestamp()),
                           str(summary), str(location)))

    return sorted(events, key=lambda event: event[0]), target_day
