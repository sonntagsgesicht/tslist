
import sys
from urllib.parse import quote_plus


from tslist import TSDict


class TSClient:
    TIMEOUT = 30

    def __init__(self, path='', *, verbose=1, token='',
                 host='127.0.0.1', port='5000'):
        """|TSDir| like client for remote |TSDir|

        :param path: route to data on remote directory
        :param verbose: verbosity of logging
        :param token: token to access remote directory
        :param host: host address of remote directory
        :param port: port of remote directory

        >>> from tslist import api, TSClient

        To start a remote directory run

        .. code-block:: bash

            $ python -m flask --app "tslist:api('DB/ROUTE', 'token1', ...)" run

        For more about runnig a flask server
        see `flask <https://flask.palletsprojects.com/en/stable/>`_

        >>> client = TSClient('DB/ROUTE', token='token1')
        >>> client
        TSClient('DB/ROUTE', verbose=1, token='token1', host='127.0.0.1', port='5000')

        >>> client.subdir()  # doctest: +SKIP
        ['SUBDIR1', 'SUBDIR2']

        >>> client.tree()  # doctest: +SKIP
        ROUTE
        ├─ SUBDIR1 [2025-01-01 ... 2025-01-05] [5]
        └─ SUBDIR2 [2025-01-01 ... 2025-01-05] [5]

        >>> sub = client('SUBDIR1')
        >>> sub
        TSClient('DB/ROUTE/SUBDIR1', verbose=1, token='token1', host='127.0.0.1', port='5000')

        >>> sub['2025-01-03']  # doctest: +SKIP
        {'object at': '2025-01-03'}

        >>> sub['2025-01-03': '2025-01-04']  # doctest: +SKIP
        {
            '2025-01-03': {'object at': '2025-01-03'},
            '2025-01-04': {'object at': '2025-01-04'}
        }

        """  # noqa E501
        self._ = str(path)
        self.token = str(token)
        self.host = str(host)
        self.port = str(port)
        self.verbose = verbose
        self.cc = None

    @property
    def name(self):
        return self._.split('/')[-1]

    @property
    def path(self):
        return self._

    @property
    def url(self):
        if self.host.startswith('http'):
            return f"{self.host}:{self.port}/{self.path}"
        return f"http://{self.host}:{self.port}/{self.path}"

    def _log(self, *msg, sep=', ', end='\n'):
        if self.verbose:
            print(*msg, sep=sep, end=end)

    def _warn(self, *msg, sep=', ', end='\n'):
        if 1 < self.verbose:
            raise ConnectionError(*msg)
        print(*msg, sep=sep, end=end, file=sys.stderr)

    def _update(self, iterable):
        if self.cc:
            self.cc(self.path).update(iterable)

    def _get(self, *args, **kwargs):
        try:
            import requests
        except ImportError:
            raise ImportError("'client' requires 'requests' to be installed. "
                              "Consider 'pip install requests'")
        kwargs = {k: quote_plus(v)
                  for k, v in kwargs.items() if v is not None}
        if self.token:
            kwargs['token'] = kwargs.get('token', self.token)
        url = self.url.replace(' ', '+') + "/" + "/".join(args)
        result = requests.get(url, params=kwargs, timeout=self.TIMEOUT)
        if result.status_code != 200:
            self._warn(f"{result.reason} [{result.status_code}]", result.url)
        return result

    def __getitem__(self, item):
        if isinstance(item, slice):
            result = self._get(start=item.start, stop=item.stop,
                               step=item.step)
            items = TSDict(result.json().items())
            self._update(items)
            return items
        # if isinstance(item, int):
        #     return self[::][item]
        items = self._get(item=item).json()
        self._update({item: items})
        return items

    def keys(self):
        return self[::].keys()

    def values(self):
        return self[::].values()

    def items(self):
        return self[::].items()

    def __iter__(self):
        return iter(self[::])

    def __contains__(self, item):
        return self[::].__contains__(item)

    def __len__(self):
        return self[::].__len__()

    def __bool__(self):
        return self[::].__bool__()

    def __str__(self):
        return self.url

    def __repr__(self):
        cls = self.__class__.__name__
        args = {'verbose': self.verbose, 'token': self.token,
                'host': self.host, 'port': self.port, }
        args = (f"{k}={v!r}" for k, v in args.items() if v is not None)
        return f"{cls}({self.path!r}, {', '.join(args)})"

    def __call__(self, path=None, **kwargs):
        kwargs['path'] = self.path + '/' + path
        kwargs['verbose'] = kwargs.get('verbose', self.verbose)
        kwargs['token'] = kwargs.get('token', self.token)
        kwargs['host'] = kwargs.get('host', self.host)
        kwargs['port'] = kwargs.get('port', self.port)
        return self.__class__(**kwargs)

    def subdir(self, **kwargs):
        args = list(d for d in self._get('subdir').json())
        return tuple(self(arg, **kwargs) for arg in args)

    def tree(self, print=print):
        s = self._get('tree').text
        return print(s) if print else s
