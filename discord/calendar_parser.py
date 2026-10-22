"""Fetch a single day's events from an iCal feed."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from dateutil.rrule import rrulestr, rruleset
from icalendar import Calendar

LOCALTZ = ZoneInfo('America/Toronto')
REQUEST_TIMEOUT = 30


def _localize(dt):
    """Return a timezone-aware datetime whose UTC offset follows DST.

    icalendar hands back pytz timezones, which are pinned to the offset in
    effect on that specific date. dateutil's rrule reuses the series start's
    tzinfo for every occurrence, so a 9pm series that began in winter (EST)
    would come out as 10pm once summer time (EDT) starts. zoneinfo picks the
    right offset for each date, so swap pytz zones for zoneinfo ones.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=LOCALTZ)
    zone = getattr(dt.tzinfo, 'zone', None)  # only pytz zones have .zone
    if zone:
        try:
            return dt.replace(tzinfo=ZoneInfo(zone))
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return dt


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
            dates.append(_localize(ex_dt))
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
    target_day = datetime.now(LOCALTZ) + timedelta(days=offset)
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
            startdt = datetime.combine(startdt, datetime.min.time())
        startdt = _localize(startdt)

        rrule = component.get('rrule')
        if rrule:
            recur_rule = rrule.to_ical().decode('utf-8')
            exclusions = component.get('exdate')
            for timestamp in cal_recurrences(recur_rule, startdt, exclusions,
                                             day_start, day_end):
                events.append((int(timestamp), str(summary), str(location)))
        elif day_start < startdt < day_end:
            events.append((int(startdt.timestamp()),
                           str(summary), str(location)))

    return sorted(events, key=lambda event: event[0]), target_day
