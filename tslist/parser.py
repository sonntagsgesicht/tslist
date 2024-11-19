# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from warnings import warn

from datetime import date, datetime, timedelta

try:
    from dateutil.parser import parse
except ImportError:
    def parse(date_str: str, **kwargs):
        msg = ("dateutil not found. consider 'pip install python-dateutil' "
               "for more flexible datetime parsing")
        warn(msg)
        date_str = str(date_str)
        if date_str.count('-'):
            str_format = '%Y-%m-%d'
        elif date_str.count('.'):
            str_format = '%d.%m.%Y'
        elif date_str.count('/'):
            str_format = '%m/%d/%Y'
        elif len(date_str) == 8 and date_str.isdigit():
            str_format = '%Y%m%d'
        else:
            return datetime.fromisoformat(date_str)
        return datetime.strptime(date_str, str_format)


def parse_datetime(
        item: object | str | int | float | date | datetime | None = None,
        default: object | str | int | float | date | datetime | None = None
) -> datetime:
    if item is None:
        return datetime.now() if default is None else parse_datetime(default)

    # if isinstance(item, timedelta):
    #     return parse_datetime(default) + item

    # use date construction attribute from item
    if hasattr(item, '__ts__'):
        item = item.__ts__
        item = item() if callable(item) else item
    elif hasattr(item, '__timestamp__'):
        item = item.__timestamp__
        item = item() if callable(item) else item
    elif hasattr(item, '__date__'):
        item = item.__date__
        item = item() if callable(item) else item
    elif hasattr(item, '__datetime__'):
        item = item.__datetime__
        item = item() if callable(item) else item

    # read float as date.time
    if isinstance(item, float):
        dt, tm = str(item).split('.')
        tm = tm.ljust(6, '0')
        item = f"{dt[0:4]}-{dt[4:6]}-{dt[6:8]} {tm[0:2]}:{tm[2:4]}:{tm[4:6]}"

    # gather year, month and day from item
    if all(hasattr(item, a) for a in ('year', 'month', 'day')):
        year, month, day = item.year, item.month, item.day
        hour = getattr(item, 'hour', 0)
        minute = getattr(item, 'minute', 0)
        second = getattr(item, 'second', 0)
        microsecond = getattr(item, 'microsecond', 0)
        tzinfo = getattr(item, 'tzinfo', None)
        fold = getattr(item, 'fold', 0)
        return datetime(year, month, day, hour, minute, second,
                        microsecond, tzinfo, fold=fold)

    # parse datetime from string
    return parse(str(item))


def parse_timedelta(
        item: str, with_months: bool | type = False
) -> timedelta:
    """parsing string to timedelta

    :param item: string to parse
    :param with_months: subtype of 'timedelta' witch admits a 'month' argument
    :return: timedelta or subtype of timedelta instance

    >>> from tslist.parser import parse_timedelta

    >>> parse_timedelta('1.3 days')
    datetime.timedelta(days=1, seconds=25920)

    >>> parse_timedelta('-1s4µs')
    datetime.timedelta(days=-1, seconds=86399, microseconds=4)

    >>> parse_timedelta('2 hours 4 Minutes 8 Sec')
    datetime.timedelta(seconds=7448)

    >>> parse_timedelta('2h4i8s')
    datetime.timedelta(seconds=7448)

    >>> with_months = lambda *_, months=0: print(timedelta(*_), months)
    >>> parse_timedelta('1y 3quarters 1m', with_months=with_months)
    0:00:00 22.0

    """
    # can even parse strings
    # like '-2Y-4Q+5M' but also '0B', '-1Y2M3D' as well.
    item = item.lower()
    item = item.replace('and', '')
    item = item.replace('_', '')
    item = item.replace(',', '')
    item = item.replace(' ', '')
    item = item.replace('years', 'y')
    item = item.replace('quarters', 'q')
    item = item.replace('months', 'm')
    item = item.replace('weeks', 'w')
    item = item.replace('days', 'd')
    item = item.replace('hours', 'h')
    item = item.replace('minutes', 'i')
    item = item.replace('min', 'i')
    item = item.replace('seconds', 's')
    item = item.replace('sec', 's')
    item = item.replace('microseconds', 'μ')
    item = item.replace('µs', 'μ')
    item = item.replace('μs', 'μ')

    def _parse(p, letter):
        if p.find(letter) >= 0:
            s, p = p.split(letter, 1)
            s = s[1:] if s.startswith('+') else s
            sgn, s = (-1, s[1:]) if s.startswith('-') else (1, s)
            if not s.replace(".", "").isdigit():
                raise ValueError(f"Unable to parse {s} in {p}")
            return sgn * float(s), p
        return 0, p

    y, p = _parse(item, 'y')
    q, p = _parse(p, 'q')
    m, p = _parse(p, 'm')
    w, p = _parse(p, 'w')
    d, p = _parse(p, 'd')
    h, p = _parse(p, 'h')
    i, p = _parse(p, 'i')
    s, p = _parse(p, 's')
    mu, p = _parse(p, 'μ')
    if p:
        raise ValueError(f"Unable to parse {p!r}")
    m = float(m) + 3 * float(q) + 12 * float(y)
    s = (float(h) * 60 + float(i)) * 60 + float(s)
    if m:
        if not with_months:
            raise ValueError(f"found {m} months")
        return with_months(float(d), s, float(mu), months=m)
    return timedelta(float(d), s, float(mu))
