# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from datetime import datetime, date
from pprint import pformat
from typing import Callable, Any as DateType

from .parser import parse_datetime


class ts:

    def __init__(self, cls: Callable | None = None,
                 default: DateType | None = None):
        """returns timestamp in given date type"""
        self.cls = cls
        self.default = default

    def __call__(self, value: DateType | None = None):
        if self.cls is None or self.cls == datetime:
            return parse_datetime(value, self.default)
        if self.cls == date:
            return parse_datetime(value, self.default).date()
        return self.cls(value)


class TSList(list):

    def __init__(self, iterable=(), /):
        """TS filtered list

        :param iterable: iterable of items
        :return: list

        The TS filtered list enhances the standard
        `list <https://docs.python.org/3/library/stdtypes.html#list>`_
        by filtering the list by
        `slices <https://docs.python.org/3/library/stdtypes.html#slices>`_
        of types **T** differing from **int**
        in which (before comparision) any item **x**
        is converted to type **T** by calling **T(x)**

        >>> from tslist import TSList

        >>> l = 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9
        >>> tsl = TSList(l)
        >>> tsl
        TSList([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9])

        >>> tsl[1.0:1.3]  # filter all items between 1.0 (included) and 1.3 (excluded)
        TSList([1.0, 1.1, 1.2])

        >>> tsl[1.0:1.31]
        TSList([1.0, 1.1, 1.2, 1.3])

        >>> tsl[1.1]  # filter all items at 1.1
        TSList([1.1])

        >>> tsl.append(1.1)
        >>> tsl[1.1]
        TSList([1.1, 1.1])

        This becomes even more handy if list items admit conversions.

        >>> from datetime import timedelta, datetime
        >>> from tslist import TS

        >>> class Timedelta(timedelta):
        ...     def __float__(self):
        ...         return self.total_seconds()
        ...
        ...     def __ts__(self):
        ...         # used for conversion using tslist.TS
        ...         return datetime(2000, 1, 1) + self

        >>> l = [Timedelta(d) for d in range(10, 15)]
        >>> tsl = TSList(l)
        >>> tsl
        TSList(
        [ Timedelta(days=10),
          Timedelta(days=11),
          Timedelta(days=12),
          Timedelta(days=13),
          Timedelta(days=14)]
        )

        >>> list(map(float, tsl))
        [864000.0, 950400.0, 1036800.0, 1123200.0, 1209600.0]

        >>> tsl[950400.:1209600.:2]
        TSList([Timedelta(days=11), Timedelta(days=13)])

        >>> list(map(TS, tsl))
        [TS(20000111), TS(20000112), TS(20000113), TS(20000114), TS(20000115)]

        >>> tsl[TS(20000112):TS(20000114)]
        TSList([Timedelta(days=11), Timedelta(days=12)])

        See |TS()| for more detail on timestamp and datetime conversion.

        """  # noqa E501
        # todo: what if iterable is dict {ts: obj}?
        super().__init__(iterable)

    def __getitem__(self, key):

        if isinstance(key, int):
            return super().__getitem__(key)

        cls = self.__class__
        if not isinstance(key, slice):
            t = ts(key.__class__)
            return cls(v for v in self if t(v) == key)

        if isinstance(key.start, int) or isinstance(key.stop, int):
            # use default slice behavior
            return cls(super().__getitem__(key))

        if key.start and key.stop:
            t_s, t_e = ts(key.start.__class__), ts(key.stop.__class__)
            r = (v for v in self if key.start <= t_s(v) and t_e(v) < key.stop)
        elif key.start:
            t = ts(key.start.__class__)
            r = (v for v in self if key.start <= t(v))
        elif key.stop:
            t = ts(key.stop.__class__)
            r = (v for v in self if t(v) < key.stop)
        else:
            r = self

        if isinstance(key.step, int):
            # gives TSList[start:stop:step] := TSList[start:stop][::step]
            if key.step < 0:
                return cls(r)[-1::key.step]
            return cls(r)[0::key.step]
        elif key.step:
            cls = key.step.__class__.__name__
            raise ValueError(f"slice steps of type {cls!r} do not work")

        return cls(r)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        c = self.__class__.__name__
        s = super().__repr__()
        s = f"{c}({s})"
        if len(s) < 80:
            return s
        s = pformat(list(self), indent=2, sort_dicts=False)
        return f"{c}(\n{s}\n)"
