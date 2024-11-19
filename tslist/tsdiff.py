# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Sunday, 13 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from datetime import date, datetime, timedelta
from warnings import warn

from .parser import parse_timedelta


def actact(start: date, end: date):
    s, e = start.year, end.year
    if e - s == 0:
        total = datetime(s, 12, 31) - datetime(s - 1, 12, 31)
        return (end - start).total_seconds() / total.total_seconds()
    yf = e - s - 1
    start -= timedelta(1)  # since the first day counts
    yf += actact(start - timedelta(1), datetime(s, 12, 31))
    yf += actact(datetime(e, 1, 1), end)
    return yf


class TSDiff(timedelta):
    __slots__ = '_days', '_seconds', '_microseconds', '_hashcode', 'origin'

    _WARN = False

    def __new__(cls, days: int | str | timedelta = 0,
                seconds: int = 0, microseconds: int = 0, milliseconds: int = 0,
                minutes: int = 0, hours: int = 0, weeks: int = 0,
                *, origin: date | datetime = None):
        """enhanced timedelta object

        :param days:
        :param seconds:
        :param microseconds:
        :param milliseconds:
        :param minutes:
        :param hours:
        :param weeks:
        :param origin:

        Enhances `timedelta <https://docs.python.org/3/library/datetime.html#timedelta-objects>`_
        by additonal properts **origin** in order to recover difference
        of creation as

        >>> from tslist import TS, TSDiff
        >>> tsdiff = TS(20211221) - TS(20211212)
        >>> tsdiff
        TSDiff('9d', origin=TS(20211212))

        >>> tsdiff.origin
        TS(20211212)

        >>> tsdiff.origin + tsdiff
        TS(20211221)

        >>> tsdiff * 2
        datetime.timedelta(days=18)

        >>> tsdiff + tsdiff
        datetime.timedelta(days=18)


        """  # noqa E501
        if cls._WARN:
            cls._WARN = False
            warn("TSDiff implementation is still experimental")

        if isinstance(days, (int, float)):
            new = super().__new__(cls, days, seconds, microseconds,
                                  milliseconds, minutes, hours, weeks)
            new.origin = origin
            """TS diffrence origin"""
            return new

        if any((seconds, microseconds, milliseconds, minutes, hours, weeks)):
            raise ValueError("days must be int if seconds, microseconds, "
                             "milliseconds, minutes, hours or weeks given")

        if isinstance(days, timedelta):
            new = super().__new__(cls,
                                  days.days, days.seconds, days.microseconds)
            new.origin = origin or getattr(days, 'origin', None)
            return new

        new = parse_timedelta(days)
        new = super().__new__(cls, new.days, new.seconds, new.microseconds)
        new.origin = origin
        """TS diffrence origin"""
        return new

    def __float__(self):
        if self.origin is None:
            return self.total_seconds() / 86400 / 365.25
        # origin's day count
        if hasattr(self.origin, 'yf'):
            return self.origin.yf(self.origin + self)
        # actual/actual day count
        return actact(self.origin, self.origin + self)

    def _str(self):
        s = ''
        if self.days > 0:
            s += f"{self.days}d"
        if self.seconds:
            s += f"{self.seconds}s"
        if self.microseconds:
            s += f"{self.microseconds}μs"
        if self.days < 0:
            s += f"{self.days}d"
        return s

    def __str__(self):
        if self.origin:
            return f"{self.origin!r} + {self._str()!r}"
        return self._str()

    def __repr__(self):
        args = [f"{self._str()!r}"]
        if self.origin:
            args.append(f"origin={self.origin!r}")
        cls = self.__class__.__qualname__
        return f"{cls}({', '.join(args)})"
