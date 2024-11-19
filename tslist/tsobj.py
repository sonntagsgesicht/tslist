
from .ts import TS
from .tsdiff import TSDiff
from .parser import parse_timedelta, parse_datetime


class TSObject:

    def __init__(self, **kwargs):
        """generic object with key word arguments and conversion config

        :param kwargs: dict of arguments

        >>> from tslist import TS, TSObject

        setup object attributes

        >>> obj = {'a': 1, 'b': 0.0, 'c': 3, 'd': 4, 'f': '20121124', 'e': 'My Name'}

        and define dunder defaults

        >>> dunder = {'__bool__':'b', '__int__':'c', '__float__':'d', '__ts__': 'f'}

        to create object with conversion configs

        >>> d = TSObject(**obj, **dunder, __str__='e', __date__='f')
        >>>
        >>> d
        TSObject(a=1, b=0.0, c=3, d=4, f='20121124', e='My Name', __bool__='b', __int__='c', __float__='d', __ts__='f', __str__='e', __date__='f')

        Now, type conversion works as declared

        >>> repr(d)
        "TSObject(a=1, b=0.0, c=3, d=4, f='20121124', e='My Name', __bool__='b', __int__='c', __float__='d', __ts__='f', __str__='e', __date__='f')"

        >>> str(d)
        'My Name'

        >>> bool(d)
        False

        >>> int(d)
        3

        >>> float(d)
        4.0

        >>> dict(d)
        {'a': 1, 'b': 0.0, 'c': 3, 'd': 4, 'f': '20121124', 'e': 'My Name'}

        >>> list(d)
        [('a', 1), ('b', 0.0), ('c', 3), ('d', 4), ('f', '20121124'), ('e', 'My Name')]

        >>> TS(d)
        TS(20121124)

        >>> d.__date__()
        datetime.date(2012, 11, 24)

        And cloning instances works in various ways

        >>> TSObject(**d.__dict__)
        TSObject(a=1, b=0.0, c=3, d=4, f='20121124', e='My Name', __bool__='b', __int__='c', __float__='d', __ts__='f', __str__='e', __date__='f')

        >>> from copy import copy
        >>>
        >>> copy(d)
        TSObject(a=1, b=0.0, c=3, d=4, f='20121124', e='My Name', __bool__='b', __int__='c', __float__='d', __ts__='f', __str__='e', __date__='f')

        >>> from pickle import dumps, loads
        >>>
        >>> loads(dumps(d))
        TSObject(a=1, b=0.0, c=3, d=4, f='20121124', e='My Name', __bool__='b', __int__='c', __float__='d', __ts__='f', __str__='e', __date__='f')

        >>> from json import dumps, loads
        >>>
        >>> loads(dumps(dict(d)))
        {'a': 1, 'b': 0.0, 'c': 3, 'd': 4, 'f': '20121124', 'e': 'My Name'}

        """  # noqa E501
        dunder = kwargs.pop('__dunder__', {})
        dunder.update({k: v for k, v in kwargs.items()
                       if k.startswith('__') and k.endswith('__')})
        self.__dunder__ = dunder
        kwargs = {k: v for k, v in kwargs.items()
                  if not k.startswith('__') and not k.endswith('__')}
        self.__dict__.update(kwargs)

    def __iter__(self):
        return iter(v for v in self.__dict__.items() if v[0] != '__dunder__')

    def __repr__(self):
        kwargs = dict(self)
        kwargs.update(self.__dunder__)
        kwargs = (f"{k}={v!r}" for k, v in kwargs.items())
        cls = self.__class__.__qualname__
        return f"{cls}({', '.join(kwargs)})"

    def __str__(self):
        val = self.__dunder__.get('__str__', repr(self))
        return str(self.__dict__.get(str(val), val))

    def __bool__(self):
        val = self.__dunder__.get('__bool__', False)
        return bool(self.__dict__.get(str(val), val))

    def __int__(self):
        val = self.__dunder__.get('__int__', 0)
        return int(self.__dict__.get(str(val), val))

    def __float__(self):
        val = self.__dunder__.get('__float__', float(int(self)))
        return float(self.__dict__.get(str(val), val))

    def __date__(self):
        val = self.__dunder__.get('__date__')
        return parse_datetime(self.__dict__.get(str(val), val)).date()

    def __datetime__(self):
        val = self.__dunder__.get('__datetime__')
        return parse_datetime(self.__dict__.get(str(val), val))

    def __time__(self):
        val = self.__dunder__.get('__time__')
        return parse_datetime(self.__dict__.get(str(val), val)).time()

    def __timedelta__(self):
        val = self.__dunder__.get('__timedelta__')
        return parse_timedelta(self.__dict__.get(str(val), val))

    def __ts__(self):
        val = self.__dunder__.get('__ts__')
        return TS(self.__dict__.get(str(val), val))

    def __tsdiff__(self):
        val = self.__dunder__.get('__tsdiff__')
        return TSDiff(self.__dict__.get(str(val), val))
