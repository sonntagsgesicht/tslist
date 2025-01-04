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

from jedi.inference.compiled.subprocess.functions import safe_literal_eval

from .tslist import ts, TSList


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
        if not isinstance(key, (int, slice)) and key in self:
            return super().__getitem__(key)
        keys = TSList(self.keys())[key]
        if not isinstance(keys, list):
            return super().__getitem__(keys)
        items = {k: self[k] for k in keys}.items()
        return self.__class__(items)

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

    def _x__getitem__(self, key):
        if isinstance(key, int):
            key = tuple(self.keys())[key]
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
            r = (v for k, v in self.items() if key.start <= t_s(k) and t_e(k) < key.stop)
        elif key.start:
            t = ts(key.start.__class__)
            r = (v for k, v in self.items() if key.start <= t(k))
        elif key.stop:
            t = ts(key.stop.__class__)
            r = (v for k, v in self.items() if t(k) < key.stop)
        else:
            r = self.items()

        if isinstance(key.step, int):
            # gives TSList[start:stop:step] := TSList[start:stop][::step]
            if key.step < 0:
                return cls(r)[-1::key.step]
            return cls(r)[0::key.step]
        elif key.step:
            cls = key.step.__class__.__name__
            raise ValueError(f"slice steps of type {cls!r} do not work")

        return cls(r)
