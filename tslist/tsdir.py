
import os
import sys
import io
from datetime import datetime
from inspect import signature
from itertools import islice
from json import loads, dumps
from pathlib import Path
from shutil import rmtree, move

from .tslist import TSList
from .tsdict import TSDict


try:
    import pandas as pd
except ImportError:
    pd = None


NOW = None
_NO_WRITER = 'this is a read-only access'

logger = print


class TSDir:

    @classmethod
    def from_cwd(cls, cwd, *, read_only=True, verbose=1):
        """change working directory to 'cwd' and open the directory"""
        os.chdir(str(cwd))
        return cls('', read_only=read_only, verbose=verbose)

    @classmethod
    def from_home(cls, path, *, read_only=True, verbose=1):
        """open the directory relative to *home* directory"""
        return cls(Path.home().joinpath(path), read_only=read_only, verbose=verbose)  # noqa E501

    @property
    def name(self):
        """name of the directory"""
        return self._.name

    @property
    def path(self):
        """`pathlib.Path` object to the directory"""
        return self._

    def __init__(self, path: Path | str, *, read_only=True, verbose=1):
        """TS directory that behaves like a |TSDict|

        :param path: root of directory
        :param read_only: if **False** directory content may be
            created, changed and removed
            (optional; default is **True**)
        :param verbose: set level of verbosity. A value of
            *0* will be silent (no logging),
            *1* (default) will warn on errors and
            *2* will raise exceptions

        >>> from tslist import TSDir

        setup new storage directory

        >>> d = TSDir('test/TESTDIR', read_only=False)

        Create relative subdirectories by

        >>> s1 = d.sub('SUBDIR1')
        >>> s2 = d.sub('SUBDIR2')

        Add content

        >>> s1['2024-12-25'] = {'name': '1st Christmas Day'}
        >>> s1['2024-12-26'] = {'name': '2nd Christmas Day'}

        and retrieve it

        >>> s2['2024-12-24'] = {'name': 'Christmas Eve'}
        >>> s2['2024-12-31'] = {'name': 'New Years Eve'}

        >>> s1.keys()
        TSList(['2024-12-25', '2024-12-26'])

        >>> s1.values()
        ({'name': '1st Christmas Day'}, {'name': '2nd Christmas Day'})

        >>> s2[:]
        TSDict(
        { '2024-12-24': {'name': 'Christmas Eve'},
          '2024-12-31': {'name': 'New Years Eve'}}
        )

        >>> s2['2024-12-24']
        {'name': 'Christmas Eve'}

        Get an overview of all dirs and items

        >>> d.tree()
        TESTDIR
        ├─ SUBDIR1 [2024-12-25 ... 2024-12-26] (2)
        └─ SUBDIR2 [2024-12-24 ... 2024-12-31] (2)

        Remove subdir

        >>> d.remove('SUBDIR1')
        >>> d.tree()
        TESTDIR
        └─ SUBDIR2 [2024-12-24 ... 2024-12-31] (2)

        Remove even the directory itself

        >>> d.remove()
        >>> d.tree()
        <BLANKLINE>

        """
        _ = Path(path)
        if _.exists() and not _.is_dir():
            raise OSError(f"{_.absolute()} not a directory")

        self._ = _
        self.read_only = read_only
        self.verbose = verbose

        if not _.exists() and not self.read_only:
            self._.mkdir()

    def _log(self, msg=''):
        if 79 < len(msg):
            msg = msg[:75] + ' ...'
        if 1 < self.verbose:
            print(msg)

    def _warn(self, *msg, sep=', ', end='\n'):
        if 2 < self.verbose:
            raise OSError(msg)
        if 0 < self.verbose:
            print(*msg, sep=sep, end=end, file=sys.stderr)

    # --- dict type attributes ---

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, item):
        return item in self.keys()

    def __setitem__(self, key, value):
        if self.read_only:
            return self._warn(_NO_WRITER)

        if isinstance(key, slice):
            return self._warn("setting items with slice don't work here")

        if key is NOW:
            key = datetime.now().replace(microsecond=0)
        if isinstance(key, int):
            key = self.keys()[key]

        j = dumps(value, indent=2, default=str)
        self._.joinpath(key).write_text(j)

    def __getitem__(self, key):
        if isinstance(key, slice):
            keys = self.keys()[key]
            return TSDict({k: self[k] for k in keys}.items())

        if isinstance(key, int):
            key = self.keys()[key]

        j = self._.joinpath(key).read_text()
        return loads(j)

    def __delitem__(self, key):
        if self.read_only:
            return self._warn(_NO_WRITER)
        if isinstance(key, slice):
            for k in self.keys()[key]:
                del self[k]
            return
        if isinstance(key, int):
            key = self.keys()[key]

        fn = self._.joinpath(key).absolute()
        if os.path.exists(fn):
            os.remove(fn)

    def keys(self):
        """(see `dict.keys <https://docs.python.org/3/library/stdtypes.html#dict.keys>`_)"""  # noqa E501
        files = (f.name for f in self._.iterdir()
                 if f.is_file() and not f.name.startswith('.'))
        return TSList(sorted(files))

    def values(self):
        """(see `dict.values <https://docs.python.org/3/library/stdtypes.html#dict.values>`_)"""  # noqa E501
        return tuple(self[k] for k in self)

    def items(self):
        """(see `dict.items <https://docs.python.org/3/library/stdtypes.html#dict.items>`_)"""  # noqa E501
        return tuple((k, self[k]) for k in self)

    def update(self, iterable=(), **kwargs):
        """(see `dict.update <https://docs.python.org/3/library/stdtypes.html#dict.update>`_)"""  # noqa E501
        if pd and isinstance(iterable, pd.DataFrame):
            iterable = {k: i.dropna().to_dict() for k, i in iterable.items()}
        if pd and isinstance(iterable, pd.Series):
            iterable = iterable.dropna(how='all').to_dict()
        if iterable and kwargs:
            raise ValueError('Only one of `iterable` and `kwargs` is allowed')
        kwargs.update(iterable)
        for k, v in kwargs.items():
            self[k] = v

    def pop(self, key):
        """(see `dict.pop <https://docs.python.org/3/library/stdtypes.html#dict.pop>`_)"""  # noqa E501
        if isinstance(key, int):
            key = self.keys()[key]
        item = self[key]
        del self[key]
        return item

    def popitem(self, key):
        """(see `dict.popitem <https://docs.python.org/3/library/stdtypes.html#dict.popitem>`_)"""  # noqa E501
        if isinstance(key, int):
            key = self.keys()[key]
        item = key, self[key]
        del self[key]
        return item

    def setdefault(self, key, default=None):
        """(see `dict.setdefault <https://docs.python.org/3/library/stdtypes.html#dict.setdefault>`_)"""  # noqa E501
        if key not in self:
            self[key] = default

    def get(self, key, default=None):
        """(see `dict.get <https://docs.python.org/3/library/stdtypes.html#dict.get>`_)"""  # noqa E501
        try:
            return self[key]
        except KeyError:
            return default

    # --- other generic attributes ---

    def __str__(self):
        return str(self._)

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}({str(self.path)!r})"

    def __call__(self, path=None, **kwargs):
        return self.sub(path, **kwargs)

    def __getattr__(self, item):
        if not self._.joinpath('.' + item).exists():
            raise AttributeError(item)
        return self['.' + item]

    def __setattr__(self, key, value):
        slots = tuple(signature(self.__init__).parameters)
        if key.startswith('_') or key in slots:
            super().__setattr__(key, value)
        else:
            self['.' + key] = value

    def __delattr__(self, item):
        del self['.' + item]

    # --- specific attributes ---

    def sub(self, path, **kwargs):
        """opens subdirectory (and may create it)"""
        if path == '*':
            args = (d.name for d in self._.iterdir() if d.is_dir())
            return tuple(self.sub(arg, **kwargs) for arg in args)

        cls = self.__class__
        kw = {k: getattr(self, k) for k in signature(self.__init__).parameters}
        kw.update(kwargs)
        kw.pop('path', None)
        return cls(self._.joinpath(path), **kw)

    def update_map(self, iterable, func=None, key='value'):
        if func is None:
            def func(x): return {key: x}
        if pd and isinstance(iterable, (pd.DataFrame, pd.Series)):
            iterable = iterable.dropna().map(func)
        else:
            iterable = {k: func(v) for k, v in iterable.items()}
        self.update(iterable)

    def move(self, target, replace=False):
        """moves the directory to another path"""
        if self.read_only:
            return self._warn(_NO_WRITER)
        for f in self._.iterdir():
            nf = Path(target).joinpath(f.name)
            if f.is_dir():
                f.move(nf, replace=replace)
            elif replace:
                f.replace(nf)
            else:
                f.rename(nf)
        try:
            move(self._.absolute(), Path(target).absolute())
        except OSError as e:
            return self._warn(str(e))
        return self.__class__(target, read_only=self.read_only)

    def remove(self, path=''):
        """removes (deletes) the directory"""
        if self.read_only:
            return self._warn(_NO_WRITER)
        try:
            rmtree(self._.joinpath(path).absolute())
        except FileNotFoundError as e:
            return self._warn(str(e))

    def tree(self, print=print, limit=1000):
        """prints a visual tree structure of the directory"""
        space = '   '
        branch = '│  '
        tee = '├─ '
        last = '└─ '

        directories = files = 0

        def inner(dir_path: Path, prefix='', level=-1):
            nonlocal directories, files
            if not level:
                return  # 0, stop iterating
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
            contents.sort(key=lambda x: x.name)
            max_name = max([len(d.name) for d in contents], default=0)
            pointers = [tee] * (len(contents) - 1) + [last]
            for pointer, path in zip(pointers, contents):
                if path.is_dir():
                    items = [d.name for d in path.iterdir()
                             if not d.is_dir() and not d.name.startswith('.')]
                    if items:
                        files += len(items)
                        yield (prefix
                               + pointer
                               + path.name.upper().ljust(max_name)
                               + f" [{min(items)} ... {max(items)}] "
                                 f"({len(items)})")
                    else:
                        yield prefix + pointer + path.name.upper()
                    directories += 1
                    extension = branch if pointer == tee else space
                    yield from inner(path, prefix=prefix+extension, level=level-1)  # noqa E501

        s = ''
        if self._.exists():
            iterator = inner(self._)
            s = [self._.name.upper()] + list(islice(iterator, limit))
            if next(iterator, None):
                s.append(f'... length_limit, {limit}, reached')
            s = os.linesep.join(s)
        return print(s) if print else s

    def df(self, **kwargs):
        """returns items as pandas dataframe (if installed)"""
        if not pd:
            raise ImportError('pandas is not installed but required')
        j = io.StringIO(dumps(self[:], sort_keys=False))
        df = pd.read_json(j, **kwargs).T
        return df
