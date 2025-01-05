# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


from pprint import pformat

from .tslist import TSList


class TSDict(dict):

    def __init__(self, iterable=(), /, **kwargs):
        """TS filtered list

        :param iterable: iterable of items
        :return: dict

        The TS filtered dict enhances the standard
        `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_
        by filtering the dict keys by
        `slices <https://docs.python.org/3/library/stdtypes.html#slices>`_
        of types **T** differing from **int**
        in which (before comparision) any item **x**
        is converted to type **T** by calling **T(x)**

        >>> from tslist import TSDict

        >>> d = {1.0: 'a', 1.1: 'b', 1.2: 'c', 1.3: 'd', 1.4: 'e', 1.5: 'f', 1.6: 'g', 1.7: 'h', 1.8: 'i', 1.9: 'j'}
        >>> tsd = TSDict(d)
        >>> tsd
        TSDict(
        { 1.0: 'a',
          1.1: 'b',
          1.2: 'c',
          1.3: 'd',
          1.4: 'e',
          1.5: 'f',
          1.6: 'g',
          1.7: 'h',
          1.8: 'i',
          1.9: 'j'}
        )

        >>> tsd[1.3]
        'd'

        >>> tsd[1.0:1.3]  # filter all items between 1.0 (included) and 1.3 (excluded)
        TSDict({1.0: 'a', 1.1: 'b', 1.2: 'c'})

        >>> tsd[1.0:1.31]
        TSDict({1.0: 'a', 1.1: 'b', 1.2: 'c', 1.3: 'd'})

        >>> tsd[1.1]  # filter all items at 1.1
        'b'

        >>> tsd.update({1.1: 'A'})
        >>> tsd[1.1]
        'A'

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

        >>> d = {Timedelta(t): t for t in range(10, 15)}
        >>> tsd = TSDict(d)
        >>> tsd
        TSDict(
        { Timedelta(days=10): 10,
          Timedelta(days=11): 11,
          Timedelta(days=12): 12,
          Timedelta(days=13): 13,
          Timedelta(days=14): 14}
        )

        >>> list(map(float, tsd.keys()))
        [864000.0, 950400.0, 1036800.0, 1123200.0, 1209600.0]

        >>> tsd[950400.:1209600.:2]
        TSDict({Timedelta(days=11): 11, Timedelta(days=13): 13})

        >>> list(map(TS, tsd.keys()))
        [TS(20000111), TS(20000112), TS(20000113), TS(20000114), TS(20000115)]
        
        >>> tsd[TS(20000112):TS(20000114)]
        TSDict({Timedelta(days=11): 11, Timedelta(days=12): 12})
        
        See |TS()| for more detail on timestamp and datetime conversion.

        """  # noqa E501
        super().__init__(iterable, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            keys = TSList(self.keys())[key]
            items = {k: self[k] for k in keys}.items()
            return self.__class__(items)

        if isinstance(key, int):
            key = tuple(self.keys())[key]
        return super().__getitem__(key)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        c = self.__class__.__name__
        s = super().__repr__()
        s = f"{c}({s})"
        if len(s) < 80:
            return s
        s = pformat(dict(self), indent=2, sort_dicts=False)
        return f"{c}(\n{s}\n)"
