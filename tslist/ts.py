# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.1, copyright Monday, 07 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from datetime import datetime, date, timedelta, tzinfo
from warnings import warn

from .parser import parse_datetime
from .tsdiff import TSDiff


class TS(datetime):
    __slots__ = ('_year', '_month', '_day', '_hour', '_minute', '_second',
                 '_microsecond', '_tzinfo', '_hashcode', '_fold')

    _WARN = True
    DEFAULT = None

    def __new__(cls,
                year: date | datetime | str | int | float | None = None,
                month: int | None = None, day: int | None = None,
                hour: int = 0, minute: int = 0, second: int = 0,
                microsecond: int = 0, tzinfo: tzinfo | None = None,
                *, fold: int = 0):
        """variation of datetime

        :param year: (date, datetime, str, int, float or None)
            year of date or some value to parse the whole date.
            If **None** **year** is replaces by |TS.DEFAULT|,
            and if |TS.DEFAULT| is **None** |TS.now()| is retruned.
            (optional: default is **None**)
        :param month: (int or None)
        :param day: (int or None)
        :param hour: (int)
        :param minute: (int)
        :param second: (int)
        :param microsecond: (int)
        :param tzinfo: (tzinfo)
        :param fold: (int)
        """
        if cls._WARN:
            cls._WARN = False
            warn("TS implementation is still experimental")

        other = month, day, hour, minute, second, microsecond, tzinfo, fold
        if not any(other):
            item = parse_datetime(year, cls.DEFAULT)
            year, month, day = item.year, item.month, item.day
            hour = getattr(item, 'hour', 0)
            minute = getattr(item, 'minute', 0)
            second = getattr(item, 'second', 0)
            microsecond = getattr(item, 'microsecond', 0)
            tzinfo = getattr(item, 'tzinfo', None)
            fold = getattr(item, 'fold', 0)
        return super().__new__(cls, year, month, day, hour, minute, second,
                               microsecond, tzinfo, fold=fold)

    @classmethod
    def now(cls, tz: tzinfo | None = None):
        return super().now(tz)

    @classmethod
    def today(cls):
        return super().today()

    def __repr__(self):
        cls = self.__class__.__name__
        year, month, day = self.year, self.month, self.day
        hour, minute, second = self.hour, self.minute, self.second
        microsecond, tzinfo, fold = self.microsecond, self.tzinfo, self.fold
        if microsecond or tzinfo or fold:
            return f"{cls}({str(self)!r})"
        d = f"{year:04}{month:02}{day:02}"
        if hour or minute or second:
            return f"{cls}({d}.{hour:02}{minute:02}{second:02})"
        return f"{cls}({d})"

    def __float__(self):
        year, month, day = self.year, self.month, self.day
        hour, minute, second = self.hour, self.minute, self.second
        d = f"{year:04}{month:02}{day:02}.{hour:02}{minute:02}{second:02}"
        return float(d)

    def __int__(self):
        return int(float(self))

    def __copy__(self):
        return self.__class__(self)

    def __add__(self, other: timedelta):
        return super().__add__(other)

    def __sub__(self, other: date | datetime | timedelta):
        if isinstance(other, date):
            other = self.__class__(other)
            td = super().__sub__(other)
            return TSDiff(td, origin=other)
        return super().__sub__(other)
