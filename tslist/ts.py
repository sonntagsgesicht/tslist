# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Sunday, 13 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from datetime import datetime, date, tzinfo
from warnings import warn

from .parser import parse_datetime
from .tsdiff import TSDiff


class TS(datetime):
    __slots__ = ('_year', '_month', '_day', '_hour', '_minute', '_second',
                 '_microsecond', '_tzinfo', '_hashcode', '_fold')

    _WARN = False
    DEFAULT = None
    """default datetime for |TS()|; if 'None' |TS()| returns current date and time"""  # noqa F401

    def __new__(cls,
                year: date | datetime | str | int | float | object | None = None,  # noqa E501
                month: int | None = None, day: int | None = None,
                hour: int = 0, minute: int = 0, second: int = 0,
                microsecond: int = 0, tzinfo: tzinfo | None = None,
                *, fold: int = 0):
        """variation of datetime

        :param year: (date, datetime, str, int, float or None)
            year of date or some value to parse the whole date.
            If **year** is **None** it is replaces by |TS.DEFAULT|,
            and if |TS.DEFAULT| is **None** `TS.now()` is returned.
            (optional: default is **None**)
        :param month: (int or None)
        :param day: (int or None)
        :param hour: (int)
        :param minute: (int)
        :param second: (int)
        :param microsecond: (int)
        :param tzinfo: (tzinfo)
        :param fold: (int)

        |TS()| differs from datetime only by
        creating, conversion and representation.

        >>> from tslist import TS
        >>> TS.DEFAULT = 20201012
        >>> TS()
        TS(20201012)

        >>> TS('20201013')
        TS(20201013)

        >>> int(TS(20201013))
        20201013

        >>> TS(20201013.012345)
        TS(20201013.012345)

        >>> TS(20201013.012345).datetime()
        datetime.datetime(2020, 10, 13, 1, 23, 45)

        >>> TS(datetime(2020, 10, 13, 1, 23, 45))
        TS(20201013.012345)

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

    def datetime(self):
        """timestamp as standard datetime.datetime()"""
        return datetime(self.year, self.month, self.day,
                        self.hour, self.minute, self.second,
                        self.microsecond, self.tzinfo, fold=self.fold)

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

    def __add__(self, other):
        return super().__add__(other)

    def __sub__(self, other):
        if isinstance(other, date):
            other = self.__class__(other)
            td = super().__sub__(other)
            return TSDiff(td, origin=other)
        return super().__sub__(other)
