
import os
import itertools

from pathlib import Path


from .parser import parse_datetime


def gap(iterable, pp=True):
    iterable = sorted(iterable)
    d = {ts: parse_datetime(prev) - parse_datetime(ts)
         for ts, prev in zip(iterable, iterable[1:])}
    d = dict(sorted(d.items(), key=lambda x: x[1]))
    g_date, g_ts = tuple(d.items())[-1] if d else ('', 0)
    if pp:
        return f"missing {g_ts}, at most on {g_date}"
    return g_date, g_ts


def minmax(iterable, pp=True):
    min_, max_ = min(iterable), max(iterable)
    if pp:
        return f"{min_} ... {max_}"
    return min_, max_


def _brackets(iterable, sep=' '):
    brackets = '[]', '()', '||', '{}', '<>', '**', '::'
    return sep.join(s + str(i) + e for s, e, i
                    in zip(itertools.cycle(brackets), iterable))


def _join(iterable, sep='] [', start='[', stop=']'):
    return f"{start}{sep.join(iterable)}{stop}"


def _summary(dir_path: Path, *func):
    if not func:
        func = minmax, len
    items = [d.name for d in dir_path.iterdir()
             if not d.is_dir() and not d.name.startswith('.')]
    if not items:
        return ''
    if func:
        items = tuple(str(f(items)) for f in func)
        return ' ' + _join(items)
    return f" [{minmax(items)}] ({len(items)})"


def _iter(dir_path: Path, *func, prefix='', level=-1):
    space = '   '
    branch = '│  '
    tee = '├─ '
    last = '└─ '

    if level == 0:
        return  # stop iterating
    contents = [d for d in dir_path.iterdir()
                if d.is_dir() and not d.name.startswith('.')]
    contents.sort(key=lambda x: x.name)
    max_name = max([len(d.name) for d in contents], default=0)
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield (prefix + pointer + path.name.upper().ljust(max_name) +
               _summary(path, *func))
        extension = branch if pointer == tee else space
        yield from _iter(path, *func,
                         prefix=prefix + extension, level=level - 1)


def tree(dir_path: Path, *func, limit=1000):
    """prints a visual tree structure of the directory"""
    func = tuple(func)
    if dir_path.exists():
        s = [dir_path.name.upper() + _summary(dir_path, *func)]
        iterator = _iter(dir_path, *func)
        s += list(itertools.islice(iterator, limit))
        if next(iterator, None):
            s.append(f'... length_limit, {limit}, reached')
        return os.linesep.join(s)
    return ''
