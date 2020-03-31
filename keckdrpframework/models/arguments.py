# arguments.py
"""
Created on Jul 9, 2019
Significantly extended Mar 29, 2020

@author: skwok, daverumph

Arguments is a class to support both keyword and positional arguments
in a clean and convenient way.
Note that __len__ and __iter__ only allow access to the positional
arguments.  This is because dict and sequence iterators have different
behaviors, namely, dict iterators only return keys, while sequence
iterators return values.  Since it isn't possible in in some cases to
distinguish a value from a key, it doesn't make sense to provide
combined access to both positional and keyword arguments through the
same iterator.  Likewise, __len__ only counts positional arguments.
If you want to count or iterate through the keyword entries, use
len_kw or iter_kw, respectively.
Indexing, however, can be used with either numbers or strings.
Numerical indexes access positional arguments, while strings are
treated as keywords.

"""


class Arguments:
    """
    Arguments class
    Positional arguments are stored on an internal args list.
    Support is included for indexing the Arguments class.  Doing
    so only gives or sets positional arguments.  Keyword arguments
    are not accessible via the index.
    insert, append, pop and iter() of positional arguments are also
    supported via passthru
    keyword arguments can also be iterated
    """

    def __init__(self, *args, **kwargs):
        self.name = "undef"
        self._pos_args = []
        self._pos_args.extend(args)
        self.__dict__.update(kwargs)

    # access all items
    def __str__(self):
        out = []
        out.extend([f"{i}: {arg}" for i, arg in enumerate(self._pos_args)])
        out.extend([f'"{k}": {v}' for k, v in self.__dict__.items() if k != "_pos_args"])
        return ", ".join(out)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, ix):
        if isinstance(ix, str):
            return self.__dict__.__getitem__(ix)
        return self._pos_args.__getitem__(ix)

    def __setitem__(self, ix, val):
        if isinstance(ix, str):
            self.__dict__.__setitem__(ix, val)
        else:
            self._pos_args.__setitem__(ix, val)

    # access positional arguments
    def __len__(self):
        """
        count of positional arguments stored
        """
        return len(self._pos_args)

    def __iter__(self):
        """
        iterator of positional arguments
        """
        return iter(self._pos_args)

    def insert(self, ix, val):
        """
        insert a positional argument before ix
        """
        self._pos_args.insert(ix, val)

    def append(self, val):
        """
        append a positional argument at the end
        """
        self._pos_args.append(val)

    def pop(self):
        """
        return and remove the last positional argument
        """
        return self._pos_args.pop()

    def extend(self, *args):
        """
        add the supplied values to the positional arguments at the end
        """
        self._pos_args.extend(args)

    # access keyword arguments
    def iter_kw(self):
        """
        iterator of the keyword arguments
        excludes the internally used '_pos_args'
        """
        for k in self.__dict__.keys():
            if k == "_pos_args":
                continue
            yield k

    def len_kw(self):
        """
        count of keyword arguments, including 'name'
        excludes the internally used '_pos_args'
        """
        # subtract one to account for _pos_args, which
        # is excluded from iteration and shouldn't be
        # directly accessed.  "name" is counted, however.
        return max(0, self.__dict__.__len__() - 1)

    def update(self, **kwargs):
        """
        add or replace supplied arguments to the keyword arguments dictionary.
        Shouldn't update '_pos_args' using this!
        """
        self.__dict__.update(kwargs)
