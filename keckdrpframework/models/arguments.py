"""
Created on Jul 9, 2019

Added positional arguments, contributed by Dave Rumph, Mar 30, 2020.

@author: skwok
"""


class Arguments:
    """
    This is placeholder for variables.
    """

    def __init__(self, *args, **kwargs):
        self.name = "undef"
        self._args = []
        self._args.extend(args)
        self.__dict__.update(kwargs)

    def __str__(self):
        out = []
        out.extend([f"{i}: {arg}" for i, arg in enumerate(self._args)])
        out.extend([f'"{k}": {v}' for k, v in self.__dict__.items() if k != "_args"])
        return ", ".join(out)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self._args)

    def __getitem__(self, ix):
        return self._args.__getitem__(ix)

    def __setitem__(self, ix, val):
        self._args.__setitem__(ix, val)

    def insert(self, ix, val):
        self._args.insert(ix, val)

    def append(self, val):
        self._args.append(val)

    def pop(self):
        return self._args.pop()

    def __len__(self):
        return len(self._args)
