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
