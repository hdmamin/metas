from collections import namedtuple, Iterable, Mapping, UserDict
from fuzzywuzzy import fuzz, process


def Args(**kwargs):
    """Wrapper to easily create a named tuple of arguments. Functions sometimes
    return multiple values, and we have a few options to handle this: we can
    return them as a regular tuple, but it is often convenient to be able to
    reference items by name rather than position. If we want the output to be
    mutable, we can return a dictionary, but this still requires more space
    than a tuple and bracket notation is arguably less convenient than dot
    notation. We can create a new namedtuple inside the function, but this
    kind of seems like overkill to create a new type of namedtuple for each
    function.

    Instead, this lets us create a namedtuple of Args on the fly just as easily
    as making a dictionary.

    Parameters
    ----------

    Examples
    --------
    def math_summary(x, y):
        sum_ = x + y
        prod = x * y
        diff = x - y
        quotient = x / y
        return Args(sum=sum_,
                    product=prod,
                    difference=diff,
                    quotient=quotient)

    >>> results = math_summary(4, 2)
    >>> results.product

    8

    >>> results.quotient

    2

    >>> results

    Args(sum=6, product=8, difference=2, quotient=2)
    """
    args = namedtuple('Args', kwargs.keys())
    return args(*kwargs.values())


class FuzzyKeyDict(dict):
    """Dictionary that will try to find similar keys if a key is missing and
    return their corresponding values. This could be useful when working with
    embeddings, where we could try mapping missing words to a combination of
    existing words.

    Examples
    --------
    d = FuzzyKeyDict(limit=3, verbose=True)
    d['dog'] = 0
    d['cat'] = 1
    d['alley cat'] = 2
    d['pig'] = 3
    d['cow'] = 4
    d['cowbell'] = 5
    d['baby cow'] = 6

    # Keys and similarity scores for the most similar keys.
    >>> d.similar_keys('house cat')
    [('alley cat', 56), ('cat', 50), ('cowbell', 25)]

    # "house cat" not in dict so we get the values for the most similar keys.
    >>> d['house cat']
    [2, 1, 5]

    # "cat" is in dict so output is an integer rather than a list.
    >>> d['cat']
    1
    """

    def __init__(self, data=None, limit=3):
        """
        Parameters
        ----------
        data: Iterable (optional)
            Sequence of pairs, such as a dictionary or a list of tuples. If
            provided, this will be used to populate the FuzzyKeyDict.
        limit: int
            Number of similar keys to find when trying to retrieve the value
            for a missing key.
        """
        if isinstance(data, Mapping):
            for k, v in data.items():
                self[k] = v
        elif isinstance(data, Iterable):
            for k, v in data:
                self[k] = v
        self.limit = limit

    def __getitem__(self, key):
        """
        Returns
        -------
        any or list[any]: If key is present in dict, the corresponding value
            is returned. If not, the n closest keys are identified and their
            corresponding values are returned in a list (where n is defined
            by the `limit` argument specified in the constructor). Values are
            sorted in descending order by the neighboring keys' similarity to
            the missing key in.
        """
        try:
            return super().__getitem__(key)
        except KeyError:
            return [self[k] for k in self.similar_keys(key)]

    def similar_keys(self, key, return_distances=False):
        pairs = process.extract(key, self.keys(), limit=self.limit,
                                scorer=fuzz.ratio)
        if return_distances:
            return pairs
        return [p[0] for p in pairs]


class LambdaDict(UserDict):
    """Create a default dict where the default function can accept parameters.
    Whereas the defaultdict in Collections can set the default as int or list,
    here we can pass in any function where the key is the parameter.
    """

    def __init__(self, default_function):
        """
        Parameters
        ----------
        default_function: function
            When referencing a key in a LambdaDict object that has not been
            added yet, the value will be the output of this function called
            with the key passed in as an argument.
        """
        super().__init__()
        self.f = default_function

    def __missing__(self, key):
        self[key] = self.f(key)
        return self[key]
