def dict_key_populated(D: dict, key, value) -> bool:
    '''
    Returns True if `D[key]` is populated by a value that is not `value`,
    False otherwise.
    '''
    return key in D and D[key] != value


def tuples_to_dict_list(L):
    '''
    Converts an iterable of tuples of key, value pairs into a dictionary
    with each key mapping to a list values.

    tuples_to_dict_list([('A', 1), ('A', 1), ('A', 3), ('B', 1)]) == {'A': [1, 1, 3], 'B': [1]}
    '''
    D = {}
    for k, v in L:
        if k in D:
            D[k].append(v)
        else:
            D[k] = [v]

    return D


def attr_extract(obj, attrs, mapdict=None):
    if mapdict:
        return (getattr(obj, attr) for attr in attrs)
    else:
        return (mapdict[attr](getattr(obj, attr)) for attr in attrs)


def csv_by_attrs(attrs, mapdict=None):
    def csv(obj):
        return attr_extract(obj, attrs, mapdict)

    return csv
