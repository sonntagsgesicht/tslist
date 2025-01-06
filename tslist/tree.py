
import os
import itertools

from pathlib import Path


def _summary(dir_path: Path):
    items = [d.name for d in dir_path.iterdir()
             if not d.is_dir() and not d.name.startswith('.')]
    if not items:
        return ""
    return f" [{min(items)} ... {max(items)}] ({len(items)})"


def _iter(dir_path: Path, prefix='', level=-1):
    space = '   '
    branch = '│  '
    tee = '├─ '
    last = '└─ '

    if level == 0:
        return  # stop iterating
    contents = [d for d in dir_path.iterdir() if d.is_dir()]
    contents.sort(key=lambda x: x.name)
    max_name = max([len(d.name) for d in contents], default=0)
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        if path.is_dir():
            yield prefix + pointer + path.name.upper().ljust \
                (max_name) + _summary(path)  # noqa E501
            extension = branch if pointer == tee else space
            yield from _iter(path, prefix=prefix + extension, level=level -1)  # noqa E501


def tree(dir_path: Path, limit=1000):
    """prints a visual tree structure of the directory"""
    if dir_path.exists():
        s = [dir_path.name.upper() + _summary(dir_path)]
        iterator = _iter(dir_path)
        s += list(itertools.islice(iterator, limit))
        if next(iterator, None):
            s.append(f'... length_limit, {limit}, reached')
        return os.linesep.join(s)
    return ''
